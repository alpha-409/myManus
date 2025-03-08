import win32api
import win32con
import win32gui
import win32com.client
import time
import json
import os
from datetime import datetime
from comtypes import client
from ctypes import windll
from analyze_search_results import SearchAnalyzer

def open_browser_search(keyword):
    """使用Windows API打开浏览器并搜索"""
    search_url = f"https://www.bing.com/search?q={keyword}"
    try:
        win32api.ShellExecute(0, 'open', search_url, None, None, win32con.SW_MAXIMIZE)
        return True
    except Exception as e:
        print(f"打开浏览器失败: {e}")
        return False

def find_browser_window(title_part, max_retries=10, retry_interval=1):
    """查找浏览器窗口，带重试机制"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            # 寻找包含搜索关键词或常见浏览器标题的窗口
            if (title_part.lower() in window_text.lower() or
                any(x in window_text.lower() for x in ['bing', 'edge', 'chrome', 'firefox', 'search'])):
                windows.append(hwnd)
    
    for attempt in range(max_retries):
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            print(f"在第 {attempt + 1} 次尝试时找到浏览器窗口")
            return windows[0]
        
        if attempt < max_retries - 1:
            print(f"未找到浏览器窗口，{retry_interval}秒后重试... ({attempt + 1}/{max_retries})")
            time.sleep(retry_interval)
    
    print(f"在 {max_retries} 次尝试后仍未找到浏览器窗口")
    return 0

def get_clipboard_content():
    """从剪贴板获取内容"""
    import win32clipboard
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

def get_window_content(hwnd):
    """通过模拟键盘操作和剪贴板获取窗口内容"""
    try:
        # 激活窗口并等待
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(2)

        # 创建shell对象用于发送按键
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # 清空当前选择
        shell.SendKeys("{ESC}")
        time.sleep(0.5)
        
        # Tab到主要内容区
        for _ in range(3):
            shell.SendKeys("{TAB}")
            time.sleep(0.3)
        
        # 全选内容
        shell.SendKeys("^a")
        time.sleep(1)
        
        # 复制到剪贴板
        shell.SendKeys("^c")
        time.sleep(1)

        # 获取剪贴板内容
        content = get_clipboard_content()
        
        if content:
            # 处理内容，提取搜索结果
            results = []
            lines = content.split('\n')
            current_result = []
            
            for line in lines:
                line = line.strip()
                if line:
                    current_result.append(line)
                elif current_result:
                    results.append('\n'.join(current_result))
                    current_result = []
            
            if current_result:
                results.append('\n'.join(current_result))
            
            # 过滤掉太短的结果和导航元素
            results = [r for r in results if len(r) > 30 and not any(x in r.lower() for x in ['copyright', 'cookies', 'privacy', 'terms'])]
            return results
        
    except Exception as e:
        print(f"获取窗口内容失败: {e}")
    return []

def get_page_source(hwnd):
    """获取页面源代码"""
    try:
        # 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)

        # 创建shell对象用于发送按键
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # 按Ctrl+U查看源代码
        shell.SendKeys("^u")
        time.sleep(2)  # 等待源代码窗口打开
        
        # 全选源代码
        shell.SendKeys("^a")
        time.sleep(0.5)
        
        # 复制到剪贴板
        shell.SendKeys("^c")
        time.sleep(0.5)
        
        # 获取源代码
        html_content = get_clipboard_content()
        
        # 关闭源代码窗口
        shell.SendKeys("%{F4}")
        
        return html_content
    except Exception as e:
        print(f"获取源代码失败: {e}")
        return None

def save_results(keyword, results, html_content=None):
    """保存搜索结果和HTML源码"""
    if not results and not html_content:
        print("没有内容可保存")
        return False
        
    # 创建results目录
    if not os.path.exists('results'):
        os.makedirs('results')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    success = True
    
    # 保存搜索结果为JSON
    if results:
        json_filename = f"results/bing_search_win32_{timestamp}.json"
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'keyword': keyword,
                    'timestamp': timestamp,
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n搜索结果已保存到: {json_filename}")
        except Exception as e:
            print(f"保存JSON结果时出错: {str(e)}")
            success = False
    
    # 保存HTML源码
    if html_content:
        html_filename = f"results/bing_search_win32_{timestamp}.html"
        try:
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML源码已保存到: {html_filename}")
        except Exception as e:
            print(f"保存HTML源码时出错: {str(e)}")
            success = False
    
    return success

def main():
    print("Windows浏览器搜索自动化")
    print("====================")
    
    while True:
        # 获取搜索关键词
        keyword = input("\n请输入搜索关键词（直接回车退出）: ").strip()
        if not keyword:
            break
        
        # 打开浏览器进行搜索
        print(f"\n正在使用Bing搜索: {keyword}")
        if open_browser_search(keyword):
            print("浏览器已打开，等待页面加载...")
            time.sleep(3)  # 等待页面加载
            
            # 等待页面加载并查找浏览器窗口
            print("等待页面加载并查找浏览器窗口...")
            time.sleep(3)  # 先等待一段时间让浏览器启动
            
            hwnd = find_browser_window(keyword, max_retries=15, retry_interval=2)
            if hwnd:
                print("找到浏览器窗口，等待页面完全加载...")
                time.sleep(3)  # 等待页面内容加载完成
                
                # 获取搜索结果和HTML源码
                results = get_window_content(hwnd)
                print("正在获取HTML源码...")
                html_content = get_page_source(hwnd)
                
                if results or html_content:
                    if results:
                        print(f"\n找到 {len(results)} 条结果:")
                        for i, result in enumerate(results, 1):
                            print(f"\n结果 {i}:")
                            print(result[:200] + "..." if len(result) > 200 else result)
                    
                    # 保存结果和HTML
                    save_results(keyword, results, html_content)
                    
                    # 调用智谱AI分析搜索结果
                    print("\n正在使用智谱AI分析搜索结果...")
                    analyzer = SearchAnalyzer()
                    analyzer.process_search_results()
                else:
                    print("未能获取任何内容")
            else:
                print("未找到浏览器窗口")
        
        # 询问是否继续
        if input("\n是否继续搜索？(y/n): ").lower() != 'y':
            break
    
    print("\n感谢使用！")

if __name__ == "__main__":
    main()
