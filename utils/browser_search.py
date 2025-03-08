import win32api
import win32con
import win32gui
import win32com.client
import win32clipboard
import json
import os
import time
from datetime import datetime

class BrowserSearch:
    def __init__(self, search_engine="bing"):
        """初始化浏览器搜索
        
        Args:
            search_engine (str): 搜索引擎("bing"/"google"/"baidu")
        """
        self.search_urls = {
            "bing": "https://www.bing.com/search?q={}",
            "google": "https://www.google.com/search?q={}",
            "baidu": "https://www.baidu.com/s?wd={}"
        }
        self.search_engine = search_engine.lower()
        if self.search_engine not in self.search_urls:
            raise ValueError(f"Unsupported search engine: {search_engine}")

    def open_browser(self, keyword):
        """打开浏览器并搜索
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            bool: 是否成功打开浏览器
        """
        search_url = self.search_urls[self.search_engine].format(keyword)
        try:
            win32api.ShellExecute(0, 'open', search_url, None, None, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            print(f"打开浏览器失败: {e}")
            return False

    def find_window(self, keyword, max_retries=10, retry_interval=1):
        """查找浏览器窗口
        
        Args:
            keyword (str): 搜索关键词
            max_retries (int): 最大重试次数
            retry_interval (int): 重试间隔(秒)
            
        Returns:
            int: 窗口句柄,如果未找到则返回0
        """
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                # 寻找包含搜索关键词或浏览器标题的窗口
                if (keyword.lower() in window_text.lower() or
                    any(x in window_text.lower() for x in ['edge', 'chrome', 'firefox', self.search_engine])):
                    windows.append(hwnd)

        for attempt in range(max_retries):
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                return windows[0]
            
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
        
        return 0

    def get_clipboard_content(self):
        """获取剪贴板内容"""
        content = ""
        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                content = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except Exception as e:
            print(f"读取剪贴板失败: {e}")
        finally:
            win32clipboard.CloseClipboard()
        return content

    def get_page_content(self, hwnd):
        """获取页面内容
        
        Args:
            hwnd (int): 窗口句柄
            
        Returns:
            tuple: (搜索结果列表, HTML源码)
        """
        results = []
        html_content = None
        
        try:
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(2)

            shell = win32com.client.Dispatch("WScript.Shell")
            
            # 获取搜索结果
            shell.SendKeys("{ESC}")
            time.sleep(0.5)
            for _ in range(3):
                shell.SendKeys("{TAB}")
                time.sleep(0.3)
            shell.SendKeys("^a")
            time.sleep(1)
            shell.SendKeys("^c")
            time.sleep(1)

            content = self.get_clipboard_content()
            if content:
                # 处理搜索结果
                current_result = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line:
                        current_result.append(line)
                    elif current_result:
                        results.append('\n'.join(current_result))
                        current_result = []
                
                if current_result:
                    results.append('\n'.join(current_result))
                
                # 过滤无关内容
                results = [r for r in results if len(r) > 30 and 
                         not any(x in r.lower() for x in ['copyright', 'cookies', 'privacy', 'terms'])]

            # 获取HTML源码
            shell.SendKeys("^u")
            time.sleep(2)
            shell.SendKeys("^a")
            time.sleep(0.5)
            shell.SendKeys("^c")
            time.sleep(0.5)
            html_content = self.get_clipboard_content()
            shell.SendKeys("%{F4}")

        except Exception as e:
            print(f"获取页面内容失败: {e}")
        
        return results, html_content

    def save_results(self, keyword, results, html_content=None, output_dir="results"):
        """保存搜索结果
        
        Args:
            keyword (str): 搜索关键词
            results (list): 搜索结果列表
            html_content (str, optional): HTML源码
            output_dir (str): 输出目录
            
        Returns:
            tuple: (json文件路径, html文件路径)或者(None, None)
        """
        if not results and not html_content:
            return None, None
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = None
        html_path = None
        
        # 保存搜索结果
        if results:
            json_path = os.path.join(output_dir, f"search_{self.search_engine}_{timestamp}.json")
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'keyword': keyword,
                        'timestamp': timestamp,
                        'results': results
                    }, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存JSON结果失败: {e}")
                json_path = None
        
        # 保存HTML源码
        if html_content:
            html_path = os.path.join(output_dir, f"search_{self.search_engine}_{timestamp}.html")
            try:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            except Exception as e:
                print(f"保存HTML源码失败: {e}")
                html_path = None
        
        return json_path, html_path

def main():
    # 使用示例
    browser = BrowserSearch()
    
    while True:
        # 获取搜索关键词
        keyword = input("\n请输入搜索关键词(直接回车退出): ").strip()
        if not keyword:
            break
            
        # 打开浏览器搜索
        if browser.open_browser(keyword):
            print("浏览器已打开，等待页面加载...")
            time.sleep(3)
            
            # 查找浏览器窗口
            hwnd = browser.find_window(keyword)
            if hwnd:
                print("找到浏览器窗口，获取内容中...")
                time.sleep(3)
                
                # 获取页面内容
                results, html = browser.get_page_content(hwnd)
                
                if results or html:
                    # 显示搜索结果
                    if results:
                        print(f"\n找到 {len(results)} 条结果:")
                        for i, result in enumerate(results, 1):
                            print(f"\n结果 {i}:")
                            print(result[:200] + "..." if len(result) > 200 else result)
                    
                    # 保存结果
                    json_path, html_path = browser.save_results(keyword, results, html)
                    if json_path:
                        print(f"\n搜索结果已保存到: {json_path}")
                    if html_path:
                        print(f"HTML源码已保存到: {html_path}")
                else:
                    print("未能获取任何内容")
            else:
                print("未找到浏览器窗口")
    
    print("\n感谢使用！")

if __name__ == "__main__":
    main()
