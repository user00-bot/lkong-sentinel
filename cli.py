# -*- coding: utf-8 -*-
"""
LKong Sentinel CLI 命令行入口
"""
import argparse
import sys

from .crawler import crawl_lkong
from .classifier import classify
from .analyzer import analyze_demand
from .utils import merge_jsonl


def cmd_crawl(args):
    crawl_lkong(args.cookie, args.stop, args.out, args.max_pages)


def cmd_merge(args):
    merge_jsonl(args.out, args.inputs)


def cmd_classify(args):
    classify(args.raw, args.start, args.end, args.out, args.months, args.pages)


def cmd_analyze(args):
    analyze_demand(args.raw, args.start, args.end, args.out, args.top)


def cmd_report(args):
    from .reporter import make_html_report
    make_html_report(args.data, args.out, args.title, args.pages)


def cmd_export(args):
    from .exporter import export_xlsx
    export_xlsx(args.data, args.out)


def main():
    parser = argparse.ArgumentParser(description="LKong Sentinel - 龙空舆情监控工具")
    sub = parser.add_subparsers(dest="cmd")

    # crawl
    p = sub.add_parser("crawl", help="抓取龙空帖子")
    p.add_argument("--cookie", default="", help="cookie 串或文件路径")
    p.add_argument("--stop", required=True, help="停止日期 YYYY-MM-DD")
    p.add_argument("--out", required=True, help="输出 jsonl 路径")
    p.add_argument("--max-pages", type=int, default=400)
    p.set_defaults(func=cmd_crawl)

    # merge
    p = sub.add_parser("merge", help="合并 jsonl 去重")
    p.add_argument("--out", required=True)
    p.add_argument("inputs", nargs="+")
    p.set_defaults(func=cmd_merge)

    # classify
    p = sub.add_parser("classify", help="主题分类")
    p.add_argument("--raw", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--months", default="")
    p.add_argument("--pages", default="")
    p.set_defaults(func=cmd_classify)

    # analyze
    p = sub.add_parser("analyze", help="情绪穿透分析")
    p.add_argument("--raw", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--top", type=int, default=5)
    p.set_defaults(func=cmd_analyze)

    # report
    p = sub.add_parser("report", help="生成 HTML 报告")
    p.add_argument("--data", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--pages", default="")
    p.set_defaults(func=cmd_report)

    # export
    p = sub.add_parser("export", help="导出 Excel")
    p.add_argument("--data", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
