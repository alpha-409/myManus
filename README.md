# MyManus 搜索分析工具

一个基于Python的自动化搜索和分析工具，能够自动执行浏览器搜索并使用AI分析搜索结果。

## 项目结构

```
myManus/
├── utils/                # 通用工具目录
│   ├── __init__.py      # 包初始化文件
│   ├── ai_client.py     # AI调用工具
│   └── browser_search.py# 浏览器搜索工具
├── search_and_analyze.py # 组合示例程序
├── README.md            # 项目说明文档
└── results/             # 结果输出目录(运行时创建)
```

## 功能特点

### 1. AI分析工具 (utils/ai_client.py)
- 基于智谱AI的文本分析
- 支持异步调用和自定义分析模板
- 自动保存分析结果

### 2. 浏览器搜索工具 (utils/browser_search.py)
- 支持多个搜索引擎(Bing/Google/Baidu)
- 自动获取搜索结果和HTML源码
- 结果保存为JSON和HTML格式

### 3. 组合应用 (search_and_analyze.py)
- 自动执行搜索并获取结果
- 调用AI分析搜索内容
- 保存所有中间结果

## 使用方法

### 环境要求
- Python 3.9+
- 依赖包：
  - zhipuai
  - beautifulsoup4
  - pywin32
  - comtypes

### 安装依赖
```bash
pip install zhipuai beautifulsoup4 pywin32 comtypes
```

### 使用示例

1. 单独使用AI分析工具:
```bash
python -m utils.ai_client
```

2. 单独使用浏览器搜索工具:
```bash
python -m utils.browser_search
```

3. 使用组合功能(搜索+分析):
```bash
python search_and_analyze.py
```

## 输出说明

所有结果将保存在results目录下:

1. 搜索结果:
- `results/search_[engine]_[timestamp].json`: 搜索结果
- `results/search_[engine]_[timestamp].html`: 网页源码

2. 分析结果:
- `results/analysis_[timestamp].json`: AI分析结果

## 自定义配置

### 1. 更改搜索引擎
```python
browser = BrowserSearch(search_engine="google")  # 支持 "bing"/"google"/"baidu"
```

### 2. 自定义AI分析模板
```python
template = """
自定义分析模板...
{text}
"""
analysis = ai.analyze_text(text, template=template)
```

## 注意事项

1. 确保有稳定的网络连接
2. 不要中断自动化过程
3. 需要设置正确的智谱AI API密钥
4. 浏览器自动化过程中请勿操作浏览器

## 问题排查

1. 如果搜索结果获取失败:
   - 检查网络连接
   - 确认浏览器窗口未被最小化
   - 增加页面加载等待时间

2. 如果AI分析失败:
   - 检查API密钥是否正确
   - 确认网络连接状态
   - 查看错误信息进行具体排查

## License

MIT License
