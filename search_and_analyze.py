from utils import BrowserSearch, AIClient
import time
import os
import json
import re

def create_topic_dir(topic):
    """创建话题目录，避免重名
    
    Args:
        topic (str): 话题名称
        
    Returns:
        str: 话题目录路径
    """
    # 将话题转换为合法的文件夹名
    safe_topic = re.sub(r'[\\/:*?"<>|]', '_', topic)
    safe_topic = safe_topic.strip()
    
    # 基础路径
    base_path = os.path.join("results", safe_topic)
    
    # 如果目录已存在，添加时间戳
    if os.path.exists(base_path):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_path = f"{base_path}_{timestamp}"
    
    os.makedirs(base_path, exist_ok=True)
    return base_path

def process_search(browser, ai, keyword, topic_path):
    """处理单个搜索关键词
    
    Returns:
        str: 分析结果，如果失败则返回None
    """
    if browser.open_browser(keyword):
        print(f"\n正在搜索: {keyword}")
        print("浏览器已打开，等待页面加载...")
        time.sleep(3)
        
        hwnd = browser.find_window(keyword)
        if hwnd:
            print("找到浏览器窗口，获取内容中...")
            time.sleep(3)
            
            results, html = browser.get_page_content(hwnd)
            if results:
                # 保存搜索结果到话题目录
                json_path, html_path = browser.save_results(
                    keyword, 
                    results, 
                    html, 
                    topic_path
                )
                if json_path:
                    print(f"搜索结果已保存到: {json_path}")
                
                # 分析结果
                print("\n正在分析搜索结果...")
                analysis = ai.analyze_text("\n".join(results))
                
                # 保存分析结果到话题目录
                analysis_path = ai.save_analysis(
                    "\n".join(results), 
                    analysis,
                    topic_path=topic_path
                )
                print(f"分析结果已保存到: {analysis_path}")
                return analysis
    return None

def main():
    print("话题分析系统")
    print("============")
    
    # 初始化客户端
    browser = BrowserSearch()
    ai = AIClient()
    
    while True:
        # 获取分析话题
        topic = input("\n请输入要分析的话题(直接回车退出): ").strip()
        if not topic:
            break
            
        # 1. 创建话题目录
        topic_path = create_topic_dir(topic)
        print(f"\n已创建话题目录: {topic_path}")
        
        # 2. 获取搜索任务
        print("\n正在生成搜索关键词...")
        keywords = ai.get_search_tasks(topic)
        
        if not keywords:
            print("未能生成有效的搜索关键词")
            continue
            
        # 保存搜索任务
        task_path = os.path.join(topic_path, "task.json")
        with open(task_path, 'w', encoding='utf-8') as f:
            json.dump({"topic": topic, "keywords": keywords}, f, ensure_ascii=False, indent=2)
        print(f"搜索任务已保存到: {task_path}")
        
        # 3. 执行每个关键词的搜索和分析
        analyses = []
        for keyword in keywords:
            print(f"\n处理关键词: {keyword}")
            analysis = process_search(browser, ai, keyword, topic_path)
            if analysis:
                analyses.append(analysis)
        
        if analyses:
            # 4. 整合分析结果
            print("\n正在整合所有分析结果...")
            final_analysis = ai.analyze_final_results(topic, analyses)
            
            # 保存最终分析
            final_path = os.path.join(topic_path, "final_analysis.json")
            with open(final_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "topic": topic,
                    "timestamp": time.strftime("%Y%m%d_%H%M%S"),
                    "analysis": final_analysis
                }, f, ensure_ascii=False, indent=2)
            
            # 显示最终分析
            print("\n最终分析结果:")
            print("="*50)
            print(final_analysis)
            print("="*50)
            print(f"\n最终分析已保存到: {final_path}")
            
    print("\n感谢使用！")

if __name__ == "__main__":
    main()
