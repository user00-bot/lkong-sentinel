# -*- coding: utf-8 -*-
"""
工具函数：合并 jsonl、时间转换等。
"""
import argparse
import datetime
import json
import os


def merge_jsonl(output, inputs):
    """
    按 tid 合并多个抓取 jsonl 文件：同 tid 保留 lastpost 较新的一条。

    参数:
        output: 输出路径
        inputs: 输入 jsonl 路径列表

    返回:
        dict: {"input": 输入条数, "output": 输出去重后条数}
    """
    best = {}
    n_in = 0
    for p in inputs:
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            n_in += 1
            tid = r["tid"]
            lp = r.get("lastpost") or r.get("dateline") or 0
            if tid not in best or lp > (best[tid].get("lastpost") or best[tid].get("dateline") or 0):
                best[tid] = r
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        for r in best.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    result = {"input": n_in, "output": len(best)}
    print(f"合并完成: 输入 {n_in} 条 -> 去重后 {len(best)} 条")
    return result


def ts_from_date(date_str):
    """将 YYYY-MM-DD 转为毫秒时间戳"""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000


def load_cookie(arg):
    """从字符串或文件路径加载 cookie"""
    if os.path.isfile(arg):
        with open(arg, encoding="utf-8") as f:
            return f.read().strip()
    return arg


def main():
    ap = argparse.ArgumentParser(description="合并 jsonl 文件")
    ap.add_argument("--out", required=True, help="输出路径")
    ap.add_argument("inputs", nargs="+", help="输入 jsonl 文件")
    args = ap.parse_args()
    merge_jsonl(args.out, args.inputs)


if __name__ == "__main__":
    main()
