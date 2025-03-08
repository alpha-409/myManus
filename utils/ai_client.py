import os
import json
from zhipuai import ZhipuAI
import time
from pathlib import Path
from dotenv import load_dotenv

def load_api_key():
    """从环境文件加载API密钥
    
    优先从.env_local加载，如果不存在则从.env_online加载
    
    Returns:
        str: API密钥
    """
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    
    # 尝试加载本地环境文件
    local_env = root_dir / '.env_local'
    if local_env.exists():
        load_dotenv(local_env)
        return os.getenv('ZHIPUAI_API_KEY')
    
    # 加载在线环境文件
    online_env = root_dir / '.env_online'
    if online_env.exists():
        load_dotenv(online_env)
        return os.getenv('ZHIPUAI_API_KEY')
    
    raise ValueError("未找到API密钥配置文件(.env_local或.env_online)")

class AIClient:
    def __init__(self, api_key=None):
        """初始化AI客户端
        
        Args:
            api_key (str, optional): API密钥。如果为None则从环境文件加载
        """
        if api_key is None:
            api_key = load_api_key()
        self.client = ZhipuAI(api_key=api_key)

    def async_chat(self, prompt, model="glm-4-flash", max_retries=40, retry_interval=2):
        """异步调用AI进行对话
        
        Args:
            prompt (str): 输入的提示文本
            model (str): 使用的模型名称
            max_retries (int): 最大重试次数
            retry_interval (int): 重试间隔(秒)
            
        Returns:
            str: AI的回复内容
        """
        try:
            # 异步调用
            response = self.client.chat.asyncCompletions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            task_id = response.id
            task_status = response.task_status

            # 轮询等待结果
            retries = 0
            while task_status not in ["SUCCESS", "FAILED"] and retries <= max_retries:
                result_response = self.client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
                task_status = result_response.task_status
                if task_status == "SUCCESS":
                    return result_response.choices[0].message.content
                time.sleep(retry_interval)
                retries += 1

            return "Request Timeout"
        except Exception as e:
            return f"Error: {str(e)}"

    def analyze_text(self, text, template=None):
        """分析文本内容
        
        Args:
            text (str): 要分析的文本内容
            template (str, optional): 分析提示模板。如果为None则使用默认模板
            
        Returns:
            str: 分析结果
        """
        if template is None:
            template = """请对以下内容进行分析总结，包括以下几个方面：
1. 主要话题和关键信息概述
2. 相关新闻和动态（如果有）
3. 重要观点或争议（如果有）
4. 总体趋势和结论

内容：
{text}"""
        
        prompt = template.format(text=text)
        return self.async_chat(prompt)

    def get_search_tasks(self, topic):
        """为给定话题生成搜索任务
        
        Args:
            topic (str): 要分析的话题
            
        Returns:
            list: 搜索关键词列表和建议
        """
        prompt = f"""作为一个专业的研究分析师，请帮我分析以下话题，需要从哪些方面进行信息收集？
请列出5-8个具体的搜索关键词。每个关键词都应该针对话题的一个重要方面。
格式要求：必须输出JSON格式，包含keywords数组字段。

话题：{topic}"""
        
        response = self.async_chat(prompt)
        try:
            # 尝试从回复中提取JSON部分
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get('keywords', [])
            return []
        except:
            return []

    def analyze_final_results(self, topic, analysis_results):
        """整合分析多个搜索结果
        
        Args:
            topic (str): 原始话题
            analysis_results (list): 各个关键词的分析结果列表
            
        Returns:
            str: 整合后的分析报告
        """
        combined_text = f"话题：{topic}\n\n各方面分析结果：\n" + "\n\n".join(analysis_results)
        
        prompt = """请基于以下搜集到的分析信息，对这个话题进行深入剖析和回答。
你的分析应该：
1. 开门见山，直接针对话题提出的问题给出分析
2. 从多个角度解释这种现象背后的原因
3. 评估这种做法的利弊
4. 对未来发展趋势和可能的改进方向提出建议

请记住始终围绕原话题展开分析，确保回答切中要害。

话题：{topic}

分析信息：
{text}"""
        
        return self.async_chat(prompt.format(topic=topic, text=combined_text))

    def save_analysis(self, text, analysis, output_dir="results", timestamp=None, topic_path=None):
        """保存分析结果
        
        Args:
            text (str): 原始文本
            analysis (str): 分析结果
            output_dir (str): 输出目录
            timestamp (str, optional): 时间戳。如果为None则使用当前时间
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if timestamp is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
        result = {
            "timestamp": timestamp,
            "original_text": text,
            "analysis": analysis
        }
        
        # 如果提供了topic路径，则使用该路径
        if topic_path:
            output_dir = topic_path
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if timestamp is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
        result = {
            "timestamp": timestamp,
            "original_text": text,
            "analysis": analysis
        }
        
        output_path = os.path.join(output_dir, f"analysis_{timestamp}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return output_path

def main():
    # 使用示例
    client = AIClient()
    
    # 获取用户输入
    text = input("请输入要分析的文本(直接回车退出): ").strip()
    if not text:
        return
        
    # 分析文本
    print("\n正在分析文本...")
    analysis = client.analyze_text(text)
    
    # 保存结果
    output_path = client.save_analysis(text, analysis)
    
    # 显示结果
    print("\n分析结果:")
    print("="*50)
    print(analysis)
    print("="*50)
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    main()
