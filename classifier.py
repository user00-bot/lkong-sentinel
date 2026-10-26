# -*- coding: utf-8 -*-
"""
龙空起点舆情：分类与问题罗列（10 限定主题 + 1 补充类）。

相关性闸门（三层，避免只匹配"起点"二字造成系统性漏抓）：
  1. 标题含"起点"
  2. 编辑直播/连麦特征：(编辑|官号|编辑部|看稿) AND 直播词
  3. 起点专有概念（全勤/三江/智能推/白金大神等）且未提及其他平台
"""
import argparse
import collections
import datetime
import json
import os
import re

# ── 三层相关性闸门 ──────────────────────────────────────────────
EDITOR = re.compile(r"星河|好运|透明|蓬莱|拂尘|胡说|甚老师|编辑部|起点官号|官号")
QIDIAN = re.compile(r"起点|阅文")
LIVE = re.compile(
    r"直播|连麦|开播|直播间|文字整理|文字版|文字总结|总结版|记录贴|回放|切片|讲课|教学"
)
LIVE_EXCL = re.compile(r"动画|动漫|电视剧|凡人|灵境行者|诡秘之主|lol|v圈|虚拟主播")
OTHER_PLAT = re.compile(
    r"番茄|🍅|飞卢|七猫|塔读|晋江|Q阅|qq阅读|纵横|刺猬猫", re.IGNORECASE
)
EXCLUSIVE = re.compile(
    r"全勤|三江|智能推|白金|大神|天王|起点币|章节卡|入库系数|十二天王|"
    r"内投|责编|编辑组",
    re.IGNORECASE,
)

QUESTION_KW = re.compile(
    r"为什么|为何|怎么|如何|请问|求助|不懂|不理解|不明白|疑惑|困惑|啥时候|什么原因|"
    r"能解释|解释一下|谁知道|有没有人知道|求科普|求解|求教|求指点|有没有大佬|大佬解答|"
    r"懂的说说|求大佬|新人求|有没有懂|是不是|吗？|么？|呢？|能不能|可不可以",
    re.IGNORECASE,
)


def is_question(t):
    return bool(QUESTION_KW.search(t)) or t.rstrip().endswith(("？", "?"))


def gate(title):
    """三层相关性闸门"""
    if QIDIAN.search(title):
        return True
    if EDITOR.search(title) and LIVE.search(title) and not LIVE_EXCL.search(title):
        return True
    if EXCLUSIVE.search(title) and not OTHER_PLAT.search(title):
        return True
    return False


# ── 10 个限定主题 ──────────────────────────────────────────────
THEMES = [
    (
        "编辑直播/连麦",
        lambda t: bool(
            not LIVE_EXCL.search(t)
            and (
                (EDITOR.search(t) and LIVE.search(t))
                or (re.search(r"编辑|官号|编辑部|看稿", t) and LIVE.search(t))
                or re.search(
                    r"编辑.{0,4}(走了|离职|变动|调岗|新编辑|换编辑|跑路|跳槽)", t
                )
            )
        ),
    ),
    (
        "AI治理判定",
        lambda t: bool(
            re.search(r"ai|人工智能|斩杀|误杀|手搓|朱雀|检测|ai率|识别", t, re.I)
        ),
    ),
    (
        "作家等级/荣誉体系(白金/大神/天王)",
        lambda t: bool(re.search(r"白金|大神|天王|证道|十二天王", t)),
    ),
    (
        "用户等级/会员体系/定价",
        lambda t: bool(
            re.search(
                r"用户等级|用户主页|会员|vip|定价|看书贵|广告门槛|钻石|黄金盟|白银盟|舵主|盟主|"
                r"起点币|充值|摇光|开阳|玉衡|天玑|天璇|天枢|订阅费|涨价",
                t,
                re.I,
            )
        ),
    ),
    (
        "稿酬福利/分成待遇",
        lambda t: bool(
            re.search(r"全勤|稿费|分成|打赏|扶持|保底|稿酬|运营费|版税|收入|赚钱", t)
        ),
    ),
    (
        "内容管控/下架整改",
        lambda t: bool(
            re.search(r"禁言|下架|屏蔽|封禁|和谐|违禁词|审核|净网|删评|整改|查封", t)
        ),
    ),
    (
        "智能推荐/流量分配",
        lambda t: bool(
            re.search(
                r"智能推|推荐位|推荐榜|推流|算法|强推|流量|权重|限流|一轮|二轮|三轮|四轮|\bpk\b",
                t,
                re.I,
            )
        ),
    ),
    (
        "平台规则/公告/活动",
        lambda t: bool(
            re.search(r"活动|公告|点币|章节卡|折扣|满减|抽奖|领币|种瓜|切水果|拔剑|猜球|五折|半价|规则", t)
        ),
    ),
    (
        "编辑/投稿/签约疑惑",
        lambda t: bool(
            re.search(r"编辑|投稿|签约|内投|直发|过稿|拒稿|退稿|卡签|责编|组", t)
        )
        and is_question(t),
    ),
    (
        "新书期/上架/新人疑惑",
        lambda t: (
            re.search(r"新书|上架|入库|首订|均订|追读|三江|榜单|新书榜|雪藏|题材", t)
            and is_question(t)
        )
        or re.search(r"新人|入坑|攻略|贴士|萌新|新手|问答", t),
    ),
]

# ── 各主题下的问题桶 ──────────────────────────────────────────
BUCKETS = {
    "编辑直播/连麦": [
        ("官方直播与连麦（编辑部/官号）", r"编辑部|官号|起点官方|官方直播"),
        ("直播内容文字整理与观点摘要", r"文字整理|文字版|文字总结|总结版|记录贴|回放|切片|精华版|全场"),
        ("主编/编辑个人直播动态", r"星河|好运|透明|蓬莱|拂尘|胡说|甚老师"),
        ("编辑讲课与写作教学", r"讲课|教学|分享|经验|思路|锐评"),
        ("编辑流动与人事变动", r"走了|离职|跑路|换编辑|新编辑|实习"),
    ],
    "AI治理判定": [
        ("检测误杀与申诉无门", r"误杀|误判|无辜|申诉|冤枉|自证|气笑|手搓被"),
        ("处罚措施（斩杀/下榜/下架）", r"斩杀|下榜|下架|双榜|清榜|隐藏|封|处罚|处理|撤|一刀切|刀斩"),
        ("AI判定标准与检测机制", r"检测|判定|标准|比例|朱雀|ai率|怎么判|识别|误报|到底|放宽|限制"),
        ("同行举报与具体案例", r"举报|案例|名单|天王|曝光|截图|录屏|抄袭|本|哪些书|工作室"),
        ("行业影响与竞品动向", r"番茄|漫剧|行业|市场|未来|趋势|冲击|读者|用户|付费|影视|ip|版权|凉|没落"),
        ("平台AI政策与态度", r"政策|态度|禁|允许|放开|治理|支持|反对|违背|分区|合同|严打|方向|好事"),
        ("平台资源与推荐影响", r"推荐|榜|流量|签约|上架|资源"),
        ("AI写作与内容质量", r"写|文|内容|质量|水平|文笔|味道|情绪|读者|效果|八股|无聊"),
    ],
    "编辑/投稿/签约疑惑": [
        ("拒稿原因与求评估", r"拒稿|被拒|拒了|避雷|乱拒|看看|评估|问题出在|指点|品品|几拒|挑剔"),
        ("内投还是直发", r"内投|直发"),
        ("签约流程与卡签约", r"签约|过签|卡签|合同|授权|退稿"),
        ("编辑评价与选择", r"编辑|锐评|组|联系方式|邮箱|名单|实习|哪个"),
    ],
    "新书期/上架/新人疑惑": [
        ("新人攻略与经验分享", r"攻略|贴士|指南|总结|经验|建议|教学|手把手"),
        ("新书榜与榜单机制", r"新书榜|榜单|榜|排名|三江|强推"),
        ("入库与智能推流量", r"入库|智能推|流量|推荐"),
        ("新人入门与题材选择", r"新人|题材|能写|能不能|适合|传统|雪藏"),
        ("上架与订阅数据", r"上架|均订|订阅|首订|追读|成绩"),
    ],
    "稿酬福利/分成待遇": [
        ("全勤规则调整", r"全勤"),
        ("稿费与收入水平", r"稿费|收入|月收入|字数|多少钱|赚|稿酬"),
        ("分成比例与运营费", r"分成|运营费|五五|抽成|比例|渠道费"),
        ("打赏与盟主机制", r"打赏|盟主|白银|黄金|月票"),
        ("福利扶持政策", r"扶持|保底|奖励|补贴|福利"),
    ],
    "智能推荐/流量分配": [
        ("平台流量下滑", r"流量|下滑|下降|没流量|跌|没落|要死"),
        ("智能推机制变化", r"智能推|推流|推荐"),
        ("推荐位与轮次", r"推荐位|强推|一轮|二轮|三轮|四轮|三江|pk"),
        ("权重与限流", r"权重|限流|降权|打压|隐限"),
    ],
    "平台规则/公告/活动": [
        ("官方公告与处理结果", r"公告|处理结果|公示|通知|声明|规则"),
        ("运营活动与福利", r"活动|半价|赠书|领币|章节卡|抽奖|免费|折扣"),
        ("刷票与榜单治理", r"刷票|刷榜|治理"),
    ],
    "作家等级/荣誉体系(白金/大神/天王)": [
        ("评选名单与标准争议", r"名单|评选|双标|争议|标准|内部|流出"),
        ("白金大神动向", r"白金|大神|天王|证道|落选|注销|出走|离开"),
        ("等级待遇与版权", r"版权|待遇|签名|收入|改编"),
    ],
    "内容管控/下架整改": [
        ("禁言与作者权限", r"禁言|封禁|50年|拉黑|权限"),
        ("下架与屏蔽", r"下架|屏蔽|删|整改|查封"),
        ("审核尺度与净网", r"审核|净网|阉割|违禁|尺度"),
    ],
    "用户等级/会员体系/定价": [
        ("定价与看书贵", r"定价|贵|价格|收费|花钱|订阅费|涨价"),
        ("会员体系", r"会员|vip|订阅制|包月"),
        ("读者等级与成长值", r"等级|摇光|天枢|成长值|主页|lv"),
        ("起点币与章节卡", r"起点币|章节卡|充值|点币"),
        ("平台商业化与运营", r"运营|商业|付费|变现|广告|推广|拉新|流水|营销"),
    ],
}

# ── 补充类的问题桶 ────────────────────────────────────────────
SUP_BUCKETS = [
    ("平台口碑与唱衰", r"要死|没落|衰落|完蛋|愚蠢|活该|抛弃|唱衰|不行了|要凉|没救|倒闭|下坡|失望|退坑|"
     r"谁死|当务之急|再次伟大|末法|迟早免费|不死|要点脸|烂完|闹麻"),
    ("订阅/推荐/等级机制吐槽", r"订阅|推荐机制|推荐|读者等级|月票|日销|首订|均订|数据|算法"),
    ("内容质量与书荒吐槽", r"无聊|什么玩意|难看|看不下去|质量|八股|套路|同质|书荒|神作|没书|都写的"),
    ("抄袭与版权维权", r"抄袭|维权|起诉|盗版|侵权|搬运|洗稿"),
    ("平台竞争与对比", r"番茄|🍅|飞卢|七猫|竞品|对比|横向"),
    ("作者个人动态", r"发单章|离开|走了|完本|新书上架|太监|跑路"),
]


def to_post(r):
    return {
        "title": r["title"],
        "replies": r["replies"] or 0,
        "views": r["views"] or 0,
        "date": datetime.datetime.fromtimestamp(r["dateline"] / 1000).strftime("%Y-%m-%d"),
        "tid": r["tid"],
        "url": f"https://www.lkong.com/thread/{r['tid']}",
        "author": r.get("author"),
    }


def bucketize(posts, rules):
    """将帖子按规则分桶"""
    bk = collections.OrderedDict((n, []) for n, _ in rules)
    bk["其他讨论"] = []
    comp = [(n, re.compile(rr, re.I)) for n, rr in rules]
    for p in posts:
        for n, rx in comp:
            if rx.search(p["title"]):
                bk[n].append(p)
                break
        else:
            bk["其他讨论"].append(p)
    themes = []
    for bn, bp in bk.items():
        if not bp:
            continue
        bp = sorted(bp, key=lambda x: -x["replies"])
        themes.append(
            {
                "theme": bn,
                "count": len(bp),
                "total_replies": sum(x["replies"] for x in bp),
                "top_posts": [
                    {k: x[k] for k in ("title", "url", "replies", "views", "date")}
                    for x in bp[:5]
                ],
                "all_posts": [
                    {k: x[k] for k in ("title", "url", "replies", "views", "date", "author")}
                    for x in bp
                ],
            }
        )
    themes.sort(key=lambda x: (-x["total_replies"], -x["count"]))
    oth = [t for t in themes if t["theme"] == "其他讨论"]
    return [t for t in themes if t["theme"] != "其他讨论"] + oth


def classify(raw_path, start, end, out_path, months=None, pages=""):
    """
    对抓取数据进行主题分类。

    参数:
        raw_path: 合并后的 jsonl 路径
        start: 起始日期 YYYY-MM-DD（含）
        end: 截止日期 YYYY-MM-DD（含）
        out_path: 输出 JSON 路径
        months: 月份列表，如 ["2026-09", "2026-10"]，缺省自动计算
        pages: 抓取页数说明

    返回:
        dict: 分类结果
    """
    start_ts = datetime.datetime.strptime(start, "%Y-%m-%d").timestamp() * 1000
    end_ts = (
        datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)
    ).timestamp() * 1000

    if not months:
        months = []
        cur = datetime.date(int(start[:4]), int(start[5:7]), 1)
        stop = datetime.date(int(end[:4]), int(end[5:7]), 1)
        while cur <= stop:
            months.append(cur.strftime("%Y-%m"))
            cur = datetime.date(
                cur.year + (cur.month == 12), 1 if cur.month == 12 else cur.month + 1, 1
            )

    rows = [json.loads(l) for l in open(raw_path, encoding="utf-8")]
    inwin = [r for r in rows if r.get("lastpost") and start_ts <= r["lastpost"] < end_ts]
    gated = [r for r in inwin if gate(r["title"])]

    assigned = collections.OrderedDict((n, []) for n, _ in THEMES)
    unassigned = []
    for r in gated:
        for name, fn in THEMES:
            try:
                if fn(r["title"]):
                    assigned[name].append(r)
                    break
            except Exception:
                continue
        else:
            unassigned.append(r)

    cats = []
    for name, items in assigned.items():
        if not items:
            continue
        posts, seen = [], set()
        for r in items:
            if r["tid"] in seen:
                continue
            seen.add(r["tid"])
            posts.append(to_post(r))
        mc = collections.Counter(p["date"][:7] for p in posts)
        cats.append(
            {
                "name": name,
                "count": len(posts),
                "total_replies": sum(p["replies"] for p in posts),
                "total_views": sum(p["views"] for p in posts),
                "avg_replies": round(sum(p["replies"] for p in posts) / len(posts), 1),
                "monthly": [mc.get(m, 0) for m in months],
                "themes": bucketize(posts, BUCKETS.get(name, [])),
            }
        )

    sup_posts, seen2 = [], set()
    for r in unassigned:
        if not QIDIAN.search(r["title"]) or r["tid"] in seen2:
            continue
        seen2.add(r["tid"])
        sup_posts.append(to_post(r))
    if sup_posts:
        sup_posts = sorted(sup_posts, key=lambda x: -x["replies"])
        mc = collections.Counter(p["date"][:7] for p in sup_posts)
        cats.append(
            {
                "name": "其他起点相关讨论（未归入限定主题）",
                "count": len(sup_posts),
                "total_replies": sum(p["replies"] for p in sup_posts),
                "total_views": sum(p["views"] for p in sup_posts),
                "avg_replies": round(sum(p["replies"] for p in sup_posts) / len(sup_posts), 1),
                "monthly": [mc.get(m, 0) for m in months],
                "themes": bucketize(sup_posts, SUP_BUCKETS),
                "supplementary": True,
            }
        )

    cats.sort(key=lambda c: -c["count"])

    d0 = datetime.datetime.fromtimestamp(start_ts / 1000).date()
    ndays = int((end_ts - start_ts) // 86400000)
    daily = collections.OrderedDict(
        ((d0 + datetime.timedelta(days=i)).strftime("%Y-%m-%d"), 0) for i in range(ndays)
    )
    ai_daily = dict(daily)
    for r in gated:
        k = datetime.datetime.fromtimestamp(r["dateline"] / 1000).strftime("%Y-%m-%d")
        if k in daily:
            daily[k] += 1
    for r in assigned.get("AI治理判定", []):
        k = datetime.datetime.fromtimestamp(r["dateline"] / 1000).strftime("%Y-%m-%d")
        if k in ai_daily:
            ai_daily[k] += 1

    meta = {
        "total_raw_posts": len(inwin),
        "pages_note": pages,
        "date_range": f"{d0} 至 {datetime.datetime.fromtimestamp(end_ts/1000).date() - datetime.timedelta(days=1)}",
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "daily": daily,
        "ai_daily": ai_daily,
        "gated_total": len(gated),
        "theme_total": sum(c["count"] for c in cats if not c.get("supplementary")),
        "supplementary_total": sum(c["count"] for c in cats if c.get("supplementary")),
    }
    result = {"categories": cats, "months": months, "meta": meta}

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    print(f"分类完成: 窗口内 {len(inwin)} 篇, 闸门内 {len(gated)} 篇, 共 {len(cats)} 个主题")
    return result


def main():
    ap = argparse.ArgumentParser(description="龙空起点舆情分类")
    ap.add_argument("--raw", required=True, help="合并后的 jsonl 路径")
    ap.add_argument("--out", required=True, help="输出 JSON 路径")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD 含")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD 含")
    ap.add_argument("--months", default="", help="逗号分隔的月份列表")
    ap.add_argument("--pages", default="", help="抓取页数说明")
    args = ap.parse_args()
    classify(args.raw, args.start, args.end, args.out, args.months, args.pages)


if __name__ == "__main__":
    main()
