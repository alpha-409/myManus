# myManus - Windows 浏览器自动化工具

一个基于Windows API的浏览器自动化工具，可以执行搜索、获取结果并进行智能分析。

## 功能特点

- 🌐 自动化浏览器操作
  - 使用Windows API控制浏览器
  - 自动打开Bing搜索
  - 自动获取搜索结果
- 📑 结果采集与存储
  - 保存搜索结果为JSON格式
  - 保存完整HTML源码
  - 创建时间戳文件名以便追踪
- 🤖 智能分析（通过ZhipuAI）
  - 分析搜索结果内容
  - 提供主题概述
  - 识别关键信息和趋势

## 系统要求

- Windows 操作系统
- Python 3.6+
- 安装的浏览器（Edge, Chrome, 或 Firefox）

## 依赖库

```
pip install -r requirements.txt
```

主要依赖：
- win32api
- win32con
- win32gui
- win32com.client
- zhipuai
- beautifulsoup4

## 配置

1. 获取ZhipuAI API密钥
2. 在`analyze_search_results.py`中设置API密钥：
```python
api_key = "your_api_key_here"
```

## 使用方法

1. 运行主程序：
```bash
python browser_automation.py
```

2. 输入搜索关键词

3. 程序会自动：
   - 打开浏览器进行搜索
   - 获取搜索结果
   - 保存到results目录
   - 使用ZhipuAI分析结果

## 文件结构

- `browser_automation.py`: 主程序，处理浏览器自动化
- `analyze_search_results.py`: 结果分析模块，集成ZhipuAI
- `results/`: 保存搜索结果的目录
  - `*_search_win32_*.json`: 搜索结果JSON文件
  - `*_search_win32_*.html`: 搜索结果HTML文件
  - `*_analysis.json`: ZhipuAI分析结果

## 注意事项

1. 确保运行时浏览器没有被其他程序占用
2. 程序运行时请勿操作鼠标和键盘
3. 若遇到异常，请检查浏览器窗口是否正常打开

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来完善项目。

## 作者

myManus团队
