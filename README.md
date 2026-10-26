# 🕵️ 龙空哨兵 · LKong Sentinel

> 龙空论坛（lkong.com）网文江湖版舆情监控与分析工具。自动抓取、智能分类、情绪穿透、叙事线收束，一键生成可分享的 HTML 报告。

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ 功能一览

| 模块 | 功能 |
|------|------|
| **爬虫** | 自动抓取龙空网文江湖版（forum/15）帖子列表，支持增量刷新、cookie 登录、断点续抓 |
| **分类引擎** | 三层相关性闸门 + 10 个限定主题 + 问题罗列，自动归并归类 |
| **情绪穿透** | 五类需求信号打标（确定性/被看见/收入/站队/宣泄），量化底稿 |
| **叙事线收束** | 跨主题桶的事件链收束：引爆点 → 推进 → 落点，标注跨线交点 |
| **报告生成** | 单文件 HTML 报告（内嵌 Chart.js 图表 + CSV 导出按钮），可离线打开 |
| **Excel 导出** | 多 sheet 工作簿：主题汇总 / 问题清单 / 全部帖子 / 每日趋势 / 周环比 |
| **周环比** | 本周 vs 上周同口径对比，自动计算变化率 |
| **在线 Demo** | Gradio Web 界面，上传数据即可交互分析 |

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/<你的用户名>/lkong-sentinel.git
cd lkong-sentinel
pip install -r requirements.txt
```

### 基本用法

```python
from lkong_sentinel import LKongPipeline

# 初始化
pipe = LKongPipeline(cookie="你的LKONG_COOKIE")

# 第一步：抓取（增量模式，stop 设为上次覆盖日期 - 1 天）
pipe.crawl(stop="2026-10-08", output="data/lkong_incr.jsonl")

# 第二步：合并去重
pipe.merge(inputs=["data/lkong_prev.jsonl", "data/lkong_incr.jsonl"],
           output="data/lkong_merged.jsonl")

# 第三步：分类
pipe.classify(raw="data/lkong_merged.jsonl",
              start="2026-09-21", end="2026-10-12",
              output="data/report.json")

# 第四步：生成 HTML 报告
pipe.make_html(data="data/report.json",
               output="outputs/report.html",
               title="9.21–10.12")

# 第五步：导出 Excel
pipe.export_xlsx(data="data/report.json",
                 output="outputs/report.xlsx")
```

### 命令行

```bash
# 抓取
python -m lkong_sentinel.cli crawl --cookie "$COOKIE" --stop 2026-10-08 --out data/incr.jsonl

# 分类
python -m lkong_sentinel.cli classify --raw data/merged.jsonl \
    --start 2026-09-21 --end 2026-10-12 --out data/report.json

# 生成报告
python -m lkong_sentinel.cli report --data data/report.json \
    --out outputs/report.html --title "9.21–10.12"
```

---

## 🌐 在线 Demo

```bash
cd demo
pip install -r requirements.txt
python app.py
```

浏览器打开 `http://localhost:7860`，上传你的 JSON 数据即可交互式查看分析结果。

---

## 📁 项目结构

```
lkong-sentinel/
├── lkong_sentinel/          # 核心库
│   ├── __init__.py
│   ├── crawler.py           # 龙空爬虫
│   ├── classifier.py        # 主题分类引擎
│   ├── analyzer.py          # 情绪穿透分析
│   ├── reporter.py          # HTML 报告生成
│   ├── exporter.py          # Excel 导出
│   ├── storylines.py        # 叙事线收束
│   └── utils.py             # 工具函数
├── demo/                    # Gradio 在线 Demo
│   ├── app.py
│   └── requirements.txt
├── examples/                # 使用示例
│   └── quickstart.py
├── tests/                   # 单元测试
│   └── test_classifier.py
├── scripts/                 # 原始独立脚本（向下兼容）
├── requirements.txt
├── setup.py
└── README.md
```

---

## 📊 报告预览

生成的 HTML 报告包含：

- **概览卡片**：帖子总数、起点相关帖数、问题主题数
- **主题排行**：柱状图 + 可展开明细表
- **每日趋势**：折线图（起点帖 + AI 治理判定）
- **问题罗列**：每个主题下的细分问题清单，可点击直达原帖
- **周环比**：本周 vs 上周对比图表
- **热点叙事线**：事件链收束，标注跨线交点
- **CSV 导出**：主题汇总 / 问题清单 / 全部帖子

---

## 🔧 自定义主题规则

编辑 `lkong_sentinel/classifier.py` 顶部的 `THEMES` 和 `BUCKETS`：

```python
THEMES = [
    ("你的新主题", lambda t: bool(re.search(r"关键词", t))),
    ...
]
```

---

## 📄 License

MIT
