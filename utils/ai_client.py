import os
import json
from zhipuai import ZhipuAI
import time

class AIClient:
    def __init__(self, api_key="00ab92612dfb448d90e93f6578b78a3f.3Z57uuhwEkZfeLaC"):
        """初始化AI客户端"""
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

    def save_analysis(self, text, analysis, output_dir="results", timestamp=None):
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
