from utils import BrowserSearch, AIClient
import time

def main():
    print("搜索并分析示例")
    print("============")
    
    # 初始化搜索和AI客户端
    browser = BrowserSearch()
    ai = AIClient()
    
    while True:
        # 获取搜索关键词
        keyword = input("\n请输入搜索关键词(直接回车退出): ").strip()
        if not keyword:
            break
            
        # 1. 使用浏览器搜索
        if browser.open_browser(keyword):
            print("浏览器已打开，等待页面加载...")
            time.sleep(3)
            
            # 查找浏览器窗口
            hwnd = browser.find_window(keyword)
            if hwnd:
                print("找到浏览器窗口，获取内容中...")
                time.sleep(3)
                
                # 获取搜索结果
                results, html = browser.get_page_content(hwnd)
                
                if results:
                    # 保存搜索结果
                    json_path, html_path = browser.save_results(keyword, results, html)
                    if json_path:
                        print(f"\n搜索结果已保存到: {json_path}")
                    
                    # 2. 使用AI分析结果
                    print("\n正在分析搜索结果...")
                    analysis = ai.analyze_text("\n".join(results))
                    
                    # 保存分析结果
                    analysis_path = ai.save_analysis("\n".join(results), analysis)
                    
                    # 显示分析结果
                    print("\n分析结果:")
                    print("="*50)
                    print(analysis)
                    print("="*50)
                    print(f"\n分析结果已保存到: {analysis_path}")
                else:
                    print("未能获取任何搜索结果")
            else:
                print("未找到浏览器窗口")
    
    print("\n感谢使用！")

if __name__ == "__main__":
    main()
