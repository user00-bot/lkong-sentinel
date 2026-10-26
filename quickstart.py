# -*- coding: utf-8 -*-
"""
LKong Sentinel 快速入门示例
"""
import os
import sys

# 假设你的 cookie 存在环境变量里
COOKIE = os.environ.get("LKONG_COOKIE", "")

# 如果是第一次运行，先抓取
if COOKIE:
    from lkong_sentinel import crawl_lkong, merge_jsonl, classify
    
    # 1. 抓取
    crawl_lkong(cookie=COOKIE, stop="2026-10-01", out_path="data/lkong_incr.jsonl")
    
    # 2. 合并（首次运行只有一份数据，第二次起需要合并新旧数据）
    merge_jsonl(output="data/lkong_merged.jsonl", inputs=["data/lkong_incr.jsonl"])
    
    # 3. 分类
    classify(raw_path="data/lkong_merged.jsonl", 
             start="2026-09-21", end="2026-10-12",
             out_path="data/report.json",
             pages="首次抓取")
else:
    print("请设置 LKONG_COOKIE 环境变量")
    print("或者直接使用已有数据文件运行分类：")
    print("  python -m lkong_sentinel.classify --raw data/merged.jsonl --start 2026-09-21 --end 2026-10-12 --out data/report.json")

# 4. 生成 HTML 报告（只要有 report.json 就可以，不依赖 cookie）
from lkong_sentinel import make_html_report, export_xlsx

make_html_report(data_path="data/report.json", 
                 out_path="outputs/report.html",
                 title="9.21–10.12",
                 pages="首次抓取")

export_xlsx(data_path="data/report.json",
            out_path="outputs/report.xlsx")

print("完成！报告已生成到 outputs/ 目录")
