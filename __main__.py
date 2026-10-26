# -*- coding: utf-8 -*-
"""
LKong Sentinel - 龙空舆情监控与分析

## 项目简介

龙空论坛（lkong.com）网文江湖版（forum/15）的舆情监控工具。自动抓取帖子、智能分类、情绪穿透分析、叙事线收束，一键生成可分享的 HTML 报告和 Excel 工作簿。

## 核心功能

1. **爬虫**：按最后回复时间倒序抓取，支持增量刷新、cookie 登录、断点续抓
2. **分类引擎**：三层相关性闸门 + 10 个限定主题 + 问题罗列
3. **情绪穿透**：五类需求信号打标（确定性/被看见/收入/站队/宣泄）
4. **叙事线收束**：跨主题桶的事件链收束，标注跨线交点
5. **报告生成**：单文件 HTML（内嵌 Chart.js + CSV 导出），可离线打开
6. **Excel 导出**：多 sheet 工作簿

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```python
from lkong_sentinel import LKongPipeline

pipe = LKongPipeline(cookie="your_cookie")
pipe.crawl(stop="2026-10-08", output="data/incr.jsonl")
pipe.classify(start="2026-09-21", end="2026-10-12", output="data/report.json")
pipe.make_html(output="outputs/report.html", title="9.21–10.12")
```

## 项目结构

```
lkong-sentinel/
├── lkong_sentinel/       # 核心库
│   ├── __init__.py
│   ├── crawler.py        # 爬虫
│   ├── classifier.py     # 分类引擎
│   ├── analyzer.py       # 情绪穿透
│   ├── reporter.py       # HTML 报告
│   ├── exporter.py       # Excel 导出
│   ├── utils.py          # 工具函数
│   └── cli.py            # 命令行入口
├── demo/                 # Gradio 在线 Demo
├── examples/             # 使用示例
├── tests/                # 单元测试
├── scripts/              # 原始独立脚本（向下兼容）
├── requirements.txt
├── setup.py
└── README.md
```
