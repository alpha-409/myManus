import os
import json
from zhipuai import ZhipuAI
from bs4 import BeautifulSoup
import time

class SearchAnalyzer:
    def __init__(self, api_key="00ab92612dfb448d90e93f6578b78a3f.3Z57uuhwEkZfeLaC"):
        """初始化分析器"""
        self.client = ZhipuAI(api_key=api_key)

    def extract_main_content(self, html_content):
        """从HTML中提取主要内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取主要内容（这里以bing搜索结果为例）
            main_content = []
            
            # 提取搜索结果
            for result in soup.find_all(['h2', 'p', 'div'], class_=['b_algo', 'b_caption']):
                text = result.get_text().strip()
                if text:
                    main_content.append(text)
            
            return "\n".join(main_content)
        except Exception as e:
            print(f"提取内容时出错: {e}")
            return html_content

    def analyze_content(self, content):
        """使用智谱AI分析内容"""
        try:
            # 异步调用分析任务
            response = self.client.chat.asyncCompletions.create(
                model="glm-4-flash",  # 使用功能更强大的模型
                messages=[
                    {
                        "role": "user",
                        "content": f"""请对以下搜索结果进行分析总结，包括以下几个方面：
1. 主要话题和关键信息概述
2. 相关新闻和动态（如果有）
3. 重要观点或争议（如果有）
4. 总体趋势和结论

搜索内容：
{content}"""
                    }
                ],
            )
            
            task_id = response.id
            task_status = response.task_status

            # 轮询等待结果
            get_cnt = 0
            while task_status not in ["SUCCESS", "FAILED"] and get_cnt <= 40:
                result_response = self.client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
                task_status = result_response.task_status
                if task_status == "SUCCESS":
                    return result_response.choices[0].message.content
                time.sleep(2)
                get_cnt += 1

            return "Analysis Timeout"
        except Exception as e:
            return f"Analysis Error: {str(e)}"

    def process_search_results(self, results_dir="results"):
        """处理搜索结果目录下的所有文件"""
        if not os.path.exists(results_dir):
            print(f"结果目录不存在: {results_dir}")
            return

        # 获取最新的搜索结果文件
        html_files = [f for f in os.listdir(results_dir) if f.endswith('.html')]
        if not html_files:
            print("没有找到HTML文件")
            return

        # 按时间戳排序，处理最新的文件
        latest_html = sorted(html_files)[-1]
        html_path = os.path.join(results_dir, latest_html)
        json_path = html_path.replace('.html', '_analysis.json')

        print(f"正在分析文件: {latest_html}")

        # 读取HTML内容
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 提取主要内容
        main_content = self.extract_main_content(html_content)

        # 分析内容
        analysis = self.analyze_content(main_content)

        # 保存分析结果
        result = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_file": latest_html,
            "analysis": analysis
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n分析结果已保存到: {json_path}")
        print("\n分析结果概要:")
        print("="*50)
        print(analysis)
        print("="*50)

def main():
    analyzer = SearchAnalyzer()
    analyzer.process_search_results()

if __name__ == "__main__":
    main()
