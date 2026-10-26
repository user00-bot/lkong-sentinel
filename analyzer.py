# -*- coding: utf-8 -*-
"""
情绪穿透与需求洞察 · 信号层统计（代理指标）

对窗口内通过相关性闸门的帖子标题做五类需求/情绪信号打标统计，
输出篇数/占比/总回复/篇均回复 + 每类高热示例帖，作为"情绪→诉求→需求"
三层穿透的量化底稿。

重要口径:
  1. 这是标题层代理指标，不是情感打标。词表含噪声，占比只能当下限且含噪看。
  2. 本 skill 已废弃细粒度正负态度判定，此脚本也不做正负面。
  3. 输出只是底稿；最终交付物是人工写成的 markdown 洞察文档。
"""
import argparse
import datetime
import json
import os
import re
import sys

from .classifier import gate

# ── 五类信号词表 ──────────────────────────────────────────────
SIGNALS = {
    "确定性(为什么/标准/申诉/能不能)": r"为什么|为何|怎么判|标准|申诉|能不能|算不算|到底|依据|解释|凭什么|凭啥|咋判|是不是都|怎么算|规则|界定|明不明",
    "被看见/被回应(求看/指点/帮看)": r"帮我看看|帮我看|指点|品品|求评|看看|求大佬|求指点|求助|求教|有没有大佬|给看看|瞅瞅|诊断",
    "收入与上升(稿费/全勤/月入/均订)": r"稿费|全勤|月入|收入|均订|首订|分成|版税|赚钱|赚了|多少|保底|薪酬",
    "阵营/站队(对家/唱衰/转站)": r"番茄|🍅|打过来|送人头|天命|吊打|转点|转起|跑路|离开|没落|要死|凉|对家|低人一等|一等",
    "纯情绪宣泄(怒/离谱/烂/活该等)": r"怒喷|怒斥|离谱|气笑|活该|垃圾|烂|恶心|愚蠢|不要脸|要点脸|什么玩意|傻|滚|呵呵|笑死|绷不住|惊世骇俗|恐怖如斯|杀疯",
}


def analyze_demand(raw_path, start, end, out_path, top=5):
    """
    情绪穿透分析。

    参数:
        raw_path: 合并后的 jsonl 路径
        start: 起始日期 YYYY-MM-DD
        end: 截止日期 YYYY-MM-DD
        out_path: 输出 JSON 路径
        top: 每类取多少条示例帖

    返回:
        dict: 分析结果
    """
    lo = datetime.datetime.strptime(start, "%Y-%m-%d").timestamp() * 1000
    hi = lo + 86400 * 1000 * (
        (datetime.datetime.strptime(end, "%Y-%m-%d") - datetime.datetime.strptime(start, "%Y-%m-%d")).days + 1
    )

    rows = [json.loads(l) for l in open(raw_path, encoding="utf-8")]
    win = [
        r for r in rows
        if r.get("dateline") and lo <= r["dateline"] < hi and gate(r.get("title") or "")
    ]
    total = len(win)

    res = {}
    for name, pat in SIGNALS.items():
        hits = [r for r in win if re.search(pat, r["title"], re.I)]
        rep = sum(r["replies"] or 0 for r in hits)
        res[name] = {
            "count": len(hits),
            "share": len(hits) / total if total else 0,
            "replies": rep,
            "avg_replies": rep / len(hits) if hits else 0,
            "examples": [
                {
                    "title": r["title"],
                    "replies": r["replies"] or 0,
                    "date": datetime.datetime.fromtimestamp(r["dateline"] / 1000).strftime("%m-%d"),
                    "url": f"https://www.lkong.com/thread/{r['tid']}",
                }
                for r in sorted(hits, key=lambda x: -(x["replies"] or 0))[:top]
            ],
        }

    out = {
        "range": f"{start} ~ {end}",
        "window_posts": total,
        "signals": res,
        "note": "标题层代理指标，非情感打标；占比为含噪下限。真实需求强度以高热帖语义判读为准。",
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"情绪穿透分析完成: 窗口 {start}~{end} 闸门内 {total} 篇")
    return out


def main():
    ap = argparse.ArgumentParser(description="情绪穿透与需求洞察")
    ap.add_argument("--raw", required=True, help="merged jsonl")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD 含")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD 含")
    ap.add_argument("--out", required=True, help="输出 json")
    ap.add_argument("--top", type=int, default=5, help="每类取多少条示例帖")
    args = ap.parse_args()
    analyze_demand(args.raw, args.start, args.end, args.out, args.top)


if __name__ == "__main__":
    main()
