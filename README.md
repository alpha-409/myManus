# myManus a AI-Powered Topic Analysis System

一个基于智谱AI的话题分析系统，支持自动搜索信息、分析整理和生成报告。

## 功能特点

- 多角度分析：根据输入的话题自动生成多个相关搜索关键词
- 智能搜索：自动使用搜索引擎获取相关信息
- AI分析：使用智谱AI对搜索结果进行分析和总结
- 结构化存储：按话题组织存储所有搜索结果和分析报告
- 最终报告：整合多个维度的分析结果，生成完整的话题分析报告

## 安装说明

1. 克隆项目
```bash
git clone [repository-url]
cd myManus
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量

项目使用两个环境文件管理API密钥：
- `.env_local`：本地开发环境配置（不提交到git）
- `.env_online`：线上环境配置

创建`.env_local`文件（推荐）或使用`.env_online`，添加以下内容：
```
ZHIPUAI_API_KEY=your_api_key_here
```

## 使用方法

运行主程序：
```bash
python search_and_analyze.py
```

程序会提示输入要分析的话题，然后：
1. 自动生成相关搜索关键词
2. 针对每个关键词进行搜索和分析
3. 整合分析结果生成最终报告
4. 将所有结果保存到话题专属目录

## 项目结构

```
myManus/
├── search_and_analyze.py   # 主程序
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── ai_client.py       # AI分析客户端
│   └── browser_search.py  # 浏览器搜索工具
├── results/               # 分析结果存储
│   └── [话题名称]/       # 每个话题的专属目录
│       ├── task.json     # 搜索任务定义
│       ├── search_*.json # 搜索结果
│       ├── search_*.html # 搜索页面快照
│       ├── analysis_*.json # 单项分析结果
│       └── final_analysis.json # 最终分析报告
├── .env_local            # 本地环境配置（不提交）
└── .env_online          # 在线环境配置
```

## 示例输出

```json
{
  "topic": "如何看待宇树科技的机器人替代流水线工人",
  "timestamp": "20250309_015505",
  "analysis": {
    "主要发现": [...],
    "原因分析": [...],
    "利弊评估": [...],
    "未来趋势": [...],
    "建议": [...]
  }
}
```

## 环境依赖

- Python 3.8+
- zhipuai
- python-dotenv
- 其他依赖见 requirements.txt

## 注意事项

1. 不要提交 `.env_local` 文件到版本控制系统
2. 首次运行前确保配置了正确的API密钥
3. 生成的结果文件会按话题分类存储在 results 目录下
