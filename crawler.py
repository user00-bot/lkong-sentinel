# -*- coding: utf-8 -*-
"""
龙空网文江湖版（forum/15）列表抓取。

论坛按"最后回复时间 lastpost"倒序排列——窗口筛选用 lastpost，
停止条件为"整页最大 lastpost 早于 stop 日期"。趋势统计用 dateline。

用法:
  from lkong_sentinel import crawl_lkong
  crawl_lkong(cookie="...", stop="2026-10-08", out_path="data/incr.jsonl")
"""
import argparse
import datetime
import json
import os
import re
import time
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
RE_NEXT = re.compile(r'__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
SLEEP = 0.35


def load_cookie(arg):
    """从字符串或文件路径加载 cookie"""
    if os.path.isfile(arg):
        with open(arg, encoding="utf-8") as f:
            return f.read().strip()
    return arg


def fetch(page, cookie):
    """抓取单页列表"""
    req = urllib.request.Request(
        f"https://www.lkong.com/forum/15?page={page}",
        headers={"User-Agent": UA, "Cookie": cookie},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def crawl_lkong(cookie, stop, out_path, max_pages=400):
    """
    抓取龙空网文江湖版帖子列表。

    参数:
        cookie: 浏览器 cookie 串（或含 cookie 的文件路径）
        stop: 停止日期 YYYY-MM-DD，整页 lastpost 早于该日即停
        out_path: 输出 jsonl 路径
        max_pages: 最大抓取页数，默认 400

    返回:
        dict: {"total": 总条数, "pages": 实际页数, "out": 输出路径}
    """
    if not cookie:
        raise ValueError("缺少 cookie：需提供登录态 cookie 才能抓取")

    cookie_val = load_cookie(cookie)
    stop_ts = datetime.datetime.strptime(stop, "%Y-%m-%d").timestamp() * 1000

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    seen, total, page, empty = set(), 0, 1, 0

    with open(out_path, "w", encoding="utf-8") as out_f:
        while page <= max_pages:
            try:
                html = fetch(page, cookie_val)
                m = RE_NEXT.search(html)
                threads = (
                    json.loads(m.group(1))["props"]["pageProps"].get("threads") or []
                    if m
                    else []
                )
            except Exception as e:
                print(f"page {page} ERROR {e}", flush=True)
                time.sleep(1.5)
                page += 1
                continue

            if not threads:
                empty += 1
                if empty >= 3:
                    break
                page += 1
                time.sleep(SLEEP)
                continue
            empty = 0

            newc = 0
            for t in threads:
                tid = t.get("tid")
                if tid in seen:
                    continue
                seen.add(tid)
                newc += 1
                out_f.write(
                    json.dumps(
                        {
                            "tid": tid,
                            "title": t.get("title"),
                            "dateline": t.get("dateline"),
                            "lastpost": t.get("lastpost"),
                            "replies": t.get("replies"),
                            "views": t.get("views"),
                            "author": (t.get("author") or {}).get("name"),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            out_f.flush()
            total += newc

            max_last = max(t.get("lastpost", t["dateline"]) for t in threads)
            if max_last < stop_ts:
                print(f"已越过 {stop}，停止。", flush=True)
                break
            page += 1
            time.sleep(SLEEP)

    result = {"total": total, "pages": page, "out": out_path}
    print(f"抓取完成: total={total} pages={page} out={out_path}")
    return result


def main():
    ap = argparse.ArgumentParser(description="龙空网文江湖版抓取")
    ap.add_argument(
        "--cookie",
        default=os.environ.get("LKONG_COOKIE", ""),
        help="浏览器 cookie 串，或包含它的文件路径；也可用环境变量 LKONG_COOKIE",
    )
    ap.add_argument("--stop", required=True, help="YYYY-MM-DD，整页 lastpost 早于该日即停")
    ap.add_argument("--out", required=True, help="输出 jsonl 路径")
    ap.add_argument("--max-pages", type=int, default=400)
    args = ap.parse_args()
    crawl_lkong(args.cookie, args.stop, args.out, args.max_pages)


if __name__ == "__main__":
    main()
