# -*- coding: utf-8 -*-
"""
HTML 报告生成器：由分类 JSON 生成单文件 HTML 舆情报告（内嵌数据 + Chart.js）。
"""
import argparse
import json
import os
import re

TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>龙空起点舆情报告 __TITLE__</title>
<style>
:root{
  --bg:#f5f4f0; --card:#ffffff; --border:#e5e3da; --text:#2c2c2a; --text2:#5f5e5a; --text3:#888780;
  --accent:#D85A30; --accent2:#993C1D; --accent-bg:#FAECE7;
  --blue:#378ADD; --blue-bg:#E6F1FB; --gray:#8a8880; --gray-bg:#F1F0EC;
}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}
.wrap{max-width:1040px;margin:0 auto;padding:32px 20px 80px;}
header{margin-bottom:24px;}
header h1{font-size:26px;font-weight:600;margin:0 0 8px;}
header p.sub{color:var(--text2);font-size:14px;margin:0;}
.meta-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px;}
.meta-tag{background:var(--card);border:0.5px solid var(--border);border-radius:8px;padding:6px 12px;font-size:12.5px;color:var(--text2);}
.meta-tag b{color:var(--text);font-weight:600;}
.export-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.btn{background:var(--card);border:0.5px solid var(--border);border-radius:8px;padding:7px 14px;font-size:12.5px;color:var(--accent2);cursor:pointer;font-weight:500;}
.btn:hover{background:var(--accent-bg);border-color:var(--accent);}
.scope-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.scope-tag{background:var(--accent-bg);color:var(--accent2);border-radius:14px;padding:5px 12px;font-size:12.5px;font-weight:500;}
.scope-tag.sup{background:var(--gray-bg);color:var(--gray);}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:24px 0;}
.metric-card{background:var(--card);border:0.5px solid var(--border);border-radius:12px;padding:16px;}
.metric-card .num{font-size:26px;font-weight:600;color:var(--accent2);}
.metric-card .label{font-size:12.5px;color:var(--text2);margin-top:4px;}
.section{background:var(--card);border:0.5px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:20px;}
.section h2{font-size:16px;font-weight:600;margin:0 0 4px;}
.section .desc{font-size:13px;color:var(--text2);margin:0 0 16px;}
.insight-box{background:var(--accent-bg);border-left:3px solid var(--accent);border-radius:8px;padding:14px 16px;margin:14px 0;font-size:13.5px;}
.insight-box b{color:var(--accent2);}
table{width:100%;border-collapse:collapse;font-size:13px;}
th,td{padding:9px 10px;text-align:left;border-bottom:0.5px solid var(--border);}
th{color:var(--text2);font-weight:500;font-size:12.5px;white-space:nowrap;}
td.num{text-align:right;font-variant-numeric:tabular-nums;}
tr.cat-row{cursor:pointer;}
tr.cat-row:hover{background:#faf9f6;}
tr.cat-row.sup-row td{color:var(--gray);}
tr.cat-row td:first-child{display:flex;align-items:center;gap:8px;}
.rank{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:5px;background:var(--accent-bg);color:var(--accent2);font-size:11px;font-weight:600;flex-shrink:0;}
.tag-sup{background:var(--gray-bg);color:var(--gray);font-size:10px;padding:1px 5px;border-radius:4px;font-weight:600;}
.bar-cell{position:relative;}
.bar-bg{position:absolute;left:0;top:0;bottom:0;background:var(--accent-bg);border-radius:4px;z-index:0;}
.bar-bg.gray{background:var(--gray-bg);}
.bar-cell span{position:relative;z-index:1;}
.chevron{display:inline-block;width:14px;height:14px;color:var(--text3);transition:transform .15s;flex-shrink:0;}
.chevron.open{transform:rotate(90deg);}
.detail-row{display:none;}
.detail-row.open{display:table-row;}
.detail-row td{background:#faf9f6;padding:14px 16px;}
.prob-head{font-size:12.5px;font-weight:600;margin:4px 0 6px;}
.prob-head .tip{font-weight:400;color:var(--text3);}
.theme-block{border:0.5px solid var(--border);border-radius:8px;background:#fff;padding:10px 12px;margin-bottom:8px;}
.theme-title{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:6px;}
.theme-name{font-size:12.5px;font-weight:600;color:var(--accent2);}
.theme-stat{font-size:11.5px;color:var(--text3);}
.post-item{display:flex;justify-content:space-between;gap:12px;padding:5px 0;border-bottom:0.5px dashed var(--border);font-size:12.5px;}
.post-item:last-child{border-bottom:none;}
.post-title{color:var(--text);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-decoration:none;}
a.post-title:hover{color:var(--accent2);text-decoration:underline;}
.post-meta{color:var(--text3);white-space:nowrap;flex-shrink:0;}
footer{text-align:center;color:var(--text3);font-size:12px;margin-top:32px;line-height:1.8;}
.wc-name{font-size:12.5px;}
.wc-name.sup{color:var(--gray);}
.up{color:#C0392B;font-weight:600;}
.down{color:#1E8449;font-weight:600;}
.flat{color:var(--text3);}
.new-tag{background:var(--accent-bg);color:var(--accent2);font-size:10px;padding:1px 5px;border-radius:4px;font-weight:600;margin-left:6px;}
.story-line{border:0.5px solid var(--border);border-radius:10px;padding:14px 16px;margin-bottom:12px;background:#fffdfb;}
.story-line h3{font-size:14px;font-weight:600;margin:0 0 2px;color:var(--accent2);}
.story-meta{font-size:12px;color:var(--text2);margin-bottom:10px;}
.story-meta .link-note{color:var(--blue);}
.story-chain{display:flex;flex-wrap:wrap;gap:6px;align-items:stretch;}
.story-node{flex:0 1 auto;background:var(--gray-bg);border-radius:7px;padding:6px 10px;font-size:12px;display:flex;flex-direction:column;gap:2px;max-width:230px;}
.story-node .nd-day{color:var(--text3);font-size:10.5px;}
.story-node .nd-title{color:var(--text);text-decoration:none;line-height:1.35;}
.story-node .nd-title:hover{color:var(--accent2);text-decoration:underline;}
.story-node .nd-rep{color:var(--accent2);font-size:10.5px;font-weight:600;}
.story-node.trigger{background:var(--accent-bg);}
.story-node.trigger .nd-title{font-weight:600;}
.story-arrow{align-self:center;color:var(--text3);font-size:13px;flex-shrink:0;}
.story-close{font-size:12px;color:var(--text2);margin-top:9px;padding-top:8px;border-top:0.5px dashed var(--border);}
.story-close b{color:var(--accent2);}
@media (max-width:600px){.wrap{padding:20px 14px 60px;}header h1{font-size:21px;}th:nth-child(3),td:nth-child(3){display:none;}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>龙空「起点」舆情报告 · __TITLE__</h1>
  <p class="sub">数据来源：龙空网 · 网文江湖版（forum/15）。__PAGES__，覆盖该时段内全部有回复活动的主题帖</p>
  <div class="meta-row">
    <span class="meta-tag">统计区间：<b id="meta-range">-</b></span>
    <span class="meta-tag">周期内活跃帖总量：<b id="meta-raw">-</b> 篇</span>
    <span class="meta-tag">起点相关帖：<b id="meta-gated">-</b> 篇</span>
    <span class="meta-tag">生成时间：<b id="meta-gen">-</b></span>
  </div>
  <div class="export-row">
    <button class="btn" id="btnSummary">导出CSV · 主题汇总</button>
    <button class="btn" id="btnProblems">导出CSV · 问题清单</button>
    <button class="btn" id="btnPosts">导出CSV · 全部帖子</button>
    <button class="btn" id="btnStory" style="display:none;">导出CSV · 热点叙事线</button>
    __INSIGHT_BTN__
  </div>
  <div class="scope-row" id="scopeRow"></div>
</header>

<div class="cards" id="cardGrid"></div>

<div class="section" id="storySection" style="display:none;">
  <h2>本周热点话题收束 <span id="storyRange" style="font-weight:400;font-size:13px;color:var(--text2);"></span></h2>
  <p class="desc">把一周的每日热点按事件链收束成叙事线：同一编辑、同一事件、同一对象跨主题桶的帖子归为一条线。<b>引爆点 → 推进 → 落点</b>，并标注线与其他线的叙事交点（同一事件往往同时点燃多条线，这就是话题之间的关联）</p>
  <div class="insight-box" id="storyInsight"></div>
  <div id="storyList"></div>
</div>

<div class="section" id="wcSection" style="display:none;">
  <h2>周环比 <span id="wcRange" style="font-weight:400;font-size:13px;color:var(--text2);"></span></h2>
  <p class="desc">本周窗口 vs 上一自然周窗口（同一套闸门与主题口径分别分类）。变化率为相对变化率 (本期-上期)/上期；红=升、绿=降</p>
  <div class="insight-box" id="wcInsight"></div>
  <div style="position:relative;width:100%;height:340px;">
    <canvas id="wcChart" role="img" aria-label="分组柱状图：本周与上周各主题帖子数对比">数据见下表</canvas>
  </div>
  <table style="margin-top:14px;">
    <thead><tr>
      <th>主题</th><th class="num">上周帖数</th><th class="num">本周帖数</th><th class="num">帖数变化率</th>
      <th class="num">上周回复</th><th class="num">本周回复</th><th class="num">回复变化率</th>
    </tr></thead>
    <tbody id="wcTbody"></tbody>
  </table>
  <div class="prob-head" style="margin-top:16px;">本周热帖 TOP10 <span class="tip">（按回复量，点击直达原帖）</span></div>
  <div id="wcHot"></div>
</div>

<div class="section">
  <h2>限定主题：帖子数量排行</h2>
  <p class="desc">沿用既有主题口径。「其他起点相关讨论（未归入限定主题）」为补充类，用于兜住含"起点"但不符合上述主题的高热帖，避免静默丢弃</p>
  <div style="position:relative;width:100%;height:320px;">
    <canvas id="rankChart" role="img" aria-label="柱状图：各主题帖子数量排行">数据见下方表格</canvas>
  </div>
</div>

<div class="section">
  <h2>周期内每日趋势</h2>
  <p class="desc">橙色为"起点相关帖"总量，深色为其中 AI治理判定 主题</p>
  <div style="position:relative;width:100%;height:250px;">
    <canvas id="trendChart" role="img" aria-label="折线图：周期内每日起点相关帖数量">数据见下方表格</canvas>
  </div>
  <div class="insight-box" id="insightBox"></div>
</div>

<div class="section">
  <h2>分类明细：各主题下的问题罗列</h2>
  <p class="desc">点击任意一行展开该主题下的<b>问题清单</b>：按"问题主题"归并，每个问题给出涉及篇数、总回复量与代表性帖子（可点击直达龙空原帖）</p>
  <table id="detailTable">
    <thead>
      <tr>
        <th style="width:34%;">主题</th>
        <th class="num">帖子数</th>
        <th class="num">问题主题数</th>
        <th class="num">总回复</th>
        <th class="num">总浏览</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
</div>

<footer>
  本报告基于帖子标题关键词匹配自动分类与归并，可能存在个别归类偏差。<br>
  相关性口径：标题含"起点" + 编辑直播/连麦特征 + 起点专有概念（全勤·三江·智能推·白金大神等），并排除提及其他平台的帖子。
</footer>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const REPORT = __REPORT_DATA__;
const M = REPORT.meta;

document.getElementById('meta-range').textContent = M.date_range;
document.getElementById('meta-raw').textContent = M.total_raw_posts.toLocaleString();
document.getElementById('meta-gated').textContent = M.gated_total.toLocaleString();
document.getElementById('meta-gen').textContent = M.generated_at;
document.getElementById('scopeRow').innerHTML = REPORT.categories.map(c =>
  `<span class="scope-tag ${c.supplementary?'sup':''}">${c.name}</span>`).join('');

function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

const cats = REPORT.categories;
const mainCats = cats.filter(c => !c.supplementary);
const supCats = cats.filter(c => c.supplementary);
const totalThemes = cats.reduce((s,c)=>s+(c.themes||[]).length,0);

document.getElementById('cardGrid').innerHTML = [
  { num: M.gated_total.toLocaleString(), label: '起点相关帖总数' },
  { num: mainCats.reduce((s,c)=>s+c.count,0).toLocaleString(), label: '限定主题帖子数' },
  { num: totalThemes, label: '归并出的问题主题数' },
  { num: mainCats.length + ' + ' + supCats.length, label: '限定主题 + 补充类' },
].map(c => `<div class="metric-card"><div class="num">${c.num}</div><div class="label">${c.label}</div></div>`).join('');

// ---------- 热点话题收束 / 叙事线 ----------
(function(){
  const ST = M.storylines;
  if(!ST || !ST.lines || !ST.lines.length){ return; }
  document.getElementById('storySection').style.display = '';
  document.getElementById('storyRange').textContent = ST.range;
  const btnSt = document.getElementById('btnStory');
  if(btnSt){
    btnSt.style.display = '';
    btnSt.addEventListener('click', () => {
      const rows = [['叙事线','引爆点','跨线交点','落点','序','节点日','帖子标题','回复','链接']];
      ST.lines.forEach(l => l.nodes.forEach((n,i) => rows.push(
        [l.name, l.trigger, l.link, l.close, i+1, n.day, n.title, n.replies||0, n.url])));
      downloadCsv(`lkong_storylines_${ST.range.replace(/[^0-9]/g,'-')}.csv`, rows);
    });
  }
  const st = ST.stats || {};
  const totRep = ST.lines.reduce((s,l)=>s+l.nodes.reduce((a,n)=>a+(n.replies||0),0),0);
  const ranked = ST.lines.slice().sort((a,b)=>
    b.nodes.reduce((x,n)=>x+n.replies,0)-a.nodes.reduce((x,n)=>x+n.replies,0));
  const biggest = ranked[0];
  document.getElementById('storyInsight').innerHTML =
    `<b>收束结果：</b>本周 ${ST.range} 的每日热点收束为 <b>${st.n_lines}</b> 条叙事线，串联 <b>${st.n_posts}</b> 篇热帖、合计约 <b>${totRep.toLocaleString()}</b> 回复。`
    + `体量最大的是「<b>${biggest.name}</b>」（${biggest.nodes.reduce((x,n)=>x+n.replies,0).toLocaleString()} 回复），`
    + `其次是「<b>${ranked[1].name}</b>」。各线的"跨线交点"标注了同一事件同时点燃多条线的地方——那就是话题之间的叙事关联。`;

  function nodeHtml(l, n, i){
    const isTrigger = (i===0);
    const arrow = i < l.nodes.length-1 ? '<span class="story-arrow">→</span>' : '';
    return `<div class="story-node ${isTrigger?'trigger':''}">
      <span class="nd-day">${n.day}${isTrigger?' · 引爆':''}</span>
      <a class="nd-title" href="${n.url}" target="_blank" rel="noopener">${escapeHtml(n.title)}</a>
      <span class="nd-rep">${(n.replies||0).toLocaleString()} 回复</span>
    </div>${arrow}`;
  }
  document.getElementById('storyList').innerHTML = ST.lines.map(l => `
    <div class="story-line">
      <h3>${escapeHtml(l.name)}</h3>
      <div class="story-meta">跨线交点：<span class="link-note">${escapeHtml(l.link)}</span></div>
      <div class="story-chain">${l.nodes.map((n,i)=>nodeHtml(l,n,i)).join('')}</div>
      <div class="story-close"><b>落点：</b>${escapeHtml(l.close)}</div>
    </div>`).join('');
})();

// ---------- 周环比 ----------
(function(){
  const WC = M.week_compare;
  if(!WC){ return; }
  document.getElementById('wcSection').style.display = '';
  document.getElementById('wcRange').textContent = WC.cur_range + ' vs ' + WC.prev_range;

  function pct(a, b){
    if(b === 0) return a === 0 ? {t:'—', c:'flat'} : {t:'新增', c:'up'};
    const v = (a - b) / b * 100;
    const s = (v>0?'+':'') + v.toFixed(0) + '%';
    return {t: s, c: v>0 ? 'up' : (v<0 ? 'down' : 'flat')};
  }
  const T = WC.total;
  const gPct = pct(T.cur_gated, T.prev_gated);
  const rPct = pct(T.cur_replies, T.prev_replies);
  const grow = WC.categories.filter(r=>!r.supplementary)
    .slice().sort((a,b)=>((b.cur_replies-b.prev_replies)/(b.prev_replies||1))-((a.cur_replies-a.prev_replies)/(a.prev_replies||1)))[0];
  document.getElementById('wcInsight').innerHTML =
    `<b>本周概览：</b>起点相关帖 <b>${T.cur_gated}</b> 篇（上周 ${T.prev_gated}，<span class="${gPct.c}">${gPct.t}</span>）、`
    + `总回复 <b>${T.cur_replies.toLocaleString()}</b>（上周 ${T.prev_replies.toLocaleString()}，<span class="${rPct.c}">${rPct.t}</span>）。`
    + (grow ? ` 限定主题中升温最快的是「<b>${grow.name}</b>」（${grow.prev_replies}→${grow.cur_replies} 回复）。` : '');

  const rows = WC.categories;
  const chartCats = rows.slice().sort((a,b)=>b.cur_count-a.cur_count);
  new Chart(document.getElementById('wcChart'), {
    type:'bar',
    data:{ labels: chartCats.map(r=>r.name),
      datasets:[
        { label:WC.prev_range, data: chartCats.map(r=>r.prev_count), backgroundColor:'#b9b6ad', borderRadius:3, maxBarThickness:12 },
        { label:WC.cur_range, data: chartCats.map(r=>r.cur_count), backgroundColor:'#D85A30', borderRadius:3, maxBarThickness:12 }
      ] },
    options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:true, labels:{boxWidth:10, font:{size:11}}} },
      scales:{ x:{ beginAtZero:true, ticks:{color:'#5f5e5a'}, grid:{color:'rgba(0,0,0,0.06)'} },
               y:{ ticks:{color:'#2c2c2a', font:{size:10.5}}, grid:{display:false} } } }
  });

  document.getElementById('wcTbody').innerHTML = rows.map(r => {
    const c1 = pct(r.cur_count, r.prev_count), c2 = pct(r.cur_replies, r.prev_replies);
    const isNew = r.prev_count === 0 && r.cur_count > 0;
    return `<tr>
      <td class="wc-name ${r.supplementary?'sup':''}">${escapeHtml(r.name)}${r.supplementary?' <span class="tag-sup">补充</span>':''}${isNew?'<span class="new-tag">NEW</span>':''}</td>
      <td class="num">${r.prev_count}</td><td class="num"><b>${r.cur_count}</b></td>
      <td class="num ${c1.c}">${c1.t}</td>
      <td class="num">${r.prev_replies.toLocaleString()}</td><td class="num"><b>${r.cur_replies.toLocaleString()}</b></td>
      <td class="num ${c2.c}">${c2.t}</td></tr>`;
  }).join('');

  document.getElementById('wcHot').innerHTML = (WC.hot_posts||[]).map(p => `
    <div class="post-item">
      <a class="post-title" href="${p.url}" target="_blank" rel="noopener">${escapeHtml(p.title)}</a>
      <span class="post-meta">${p.date} · 回复${p.replies} · 浏览${(p.views||0).toLocaleString()}</span>
    </div>`).join('');
})();

new Chart(document.getElementById('rankChart'), {
  type:'bar',
  data:{ labels: cats.map(c=>c.name),
    datasets:[{ data: cats.map(c=>c.count),
      backgroundColor: cats.map(c=>c.supplementary?'#b9b6ad':'#D85A30'), borderRadius:4, maxBarThickness:22 }] },
  options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{display:false} },
    scales:{ x:{ beginAtZero:true, ticks:{color:'#5f5e5a'}, grid:{color:'rgba(0,0,0,0.06)'} },
             y:{ ticks:{color:'#2c2c2a', font:{size:11}}, grid:{display:false} } } }
});

const dailyKeys = Object.keys(M.daily);
new Chart(document.getElementById('trendChart'), {
  type:'line',
  data:{ labels: dailyKeys.map(k=>k.slice(5)),
    datasets:[
      { label:'起点相关帖', data: dailyKeys.map(k=>M.daily[k]),
        borderColor:'#D85A30', backgroundColor:'rgba(216,90,48,0.08)', fill:true,
        tension:0.3, pointRadius:3, pointBackgroundColor:'#D85A30' },
      { label:'AI治理判定', data: dailyKeys.map(k=>M.ai_daily[k]),
        borderColor:'#993C1D', borderDash:[4,3], fill:false,
        tension:0.3, pointRadius:2, pointBackgroundColor:'#993C1D' }
    ] },
  options:{ responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{display:true, labels:{boxWidth:12, font:{size:11}}} },
    scales:{ y:{ beginAtZero:true, ticks:{color:'#5f5e5a'}, grid:{color:'rgba(0,0,0,0.06)'} },
             x:{ ticks:{color:'#2c2c2a', font:{size:10}}, grid:{display:false} } } }
});

(function(){
  const d = M.daily, ai = M.ai_daily;
  const keys = Object.keys(d);
  const peak = keys.reduce((a,b)=> d[b]>d[a]?b:a);
  const aiSum = keys.reduce((s,k)=>s+ai[k],0);
  const topTheme = cats.filter(c=>!c.supplementary).reduce((a,b)=>(b.total_replies>a.total_replies?b:a));
  document.getElementById('insightBox').innerHTML =
    `<b>关键信号：</b>周期内起点相关帖共 <b>${M.gated_total}</b> 篇，日均 ${(M.gated_total/keys.length).toFixed(1)} 篇；`
    + `发帖量峰值在 <b>${peak}</b>（${d[peak]} 篇）。其中 AI治理判定主题 <b>${aiSum}</b> 篇。`
    + `按话题热度，本周期限定主题中讨论量最高的是「<b>${topTheme.name}</b>」（${topTheme.total_replies.toLocaleString()} 回复）。`;
})();

const maxCount = Math.max(...cats.map(c=>c.count));
const tbody = document.getElementById('tbody');
cats.forEach((cat, idx) => {
  const tr = document.createElement('tr');
  tr.className = 'cat-row' + (cat.supplementary ? ' sup-row' : '');
  const barPct = (cat.count / maxCount * 100).toFixed(1);
  tr.innerHTML = `
    <td>
      <svg class="chevron" viewBox="0 0 16 16" fill="none"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span class="rank">${idx+1}</span>
      <span>${escapeHtml(cat.name)}</span>
      ${cat.supplementary?'<span class="tag-sup">补充</span>':''}
    </td>
    <td class="num bar-cell"><span class="bar-bg ${cat.supplementary?'gray':''}" style="width:${barPct}%;"></span><span>${cat.count}</span></td>
    <td class="num">${(cat.themes||[]).length}</td>
    <td class="num">${cat.total_replies.toLocaleString()}</td>
    <td class="num">${cat.total_views.toLocaleString()}</td>`;

  const detailTr = document.createElement('tr');
  detailTr.className = 'detail-row';
  const themesHtml = (cat.themes||[]).map(t => {
    const posts = t.top_posts.map(p => `
      <div class="post-item">
        ${p.url ? `<a class="post-title" href="${p.url}" target="_blank" rel="noopener">${escapeHtml(p.title)}</a>` : `<span class="post-title">${escapeHtml(p.title)}</span>`}
        <span class="post-meta">${p.date} · 回复${p.replies} · 浏览${(p.views||0).toLocaleString()}</span>
      </div>`).join('');
    return `
      <div class="theme-block">
        <div class="theme-title">
          <span class="theme-name">${escapeHtml(t.theme)}</span>
          <span class="theme-stat">涉及 ${t.count} 篇 · 合计 ${t.total_replies.toLocaleString()} 回复</span>
        </div>
        ${posts}
      </div>`;
  }).join('');
  detailTr.innerHTML = `<td colspan="5">
    <div class="prob-head">问题罗列 <span class="tip">（按讨论热度排序，每项取该问题下回复最高的帖子）</span></div>
    ${themesHtml}</td>`;

  tr.addEventListener('click', () => {
    tr.querySelector('.chevron').classList.toggle('open');
    detailTr.classList.toggle('open');
  });
  tbody.appendChild(tr);
  tbody.appendChild(detailTr);
});

// ---------- CSV 导出 ----------
function csvCell(v){
  const s = String(v ?? '');
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g,'""') + '"' : s;
}
function downloadCsv(name, rows){
  const body = rows.map(r => r.map(csvCell).join(',')).join('\r\n');
  const blob = new Blob(['\uFEFF' + body], {type:'text/csv;charset=utf-8;'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}
const tag = (c) => c.supplementary ? '补充' : '限定';
document.getElementById('btnSummary').addEventListener('click', () => {
  const rows = [['主题','类别','帖子数','问题主题数','总回复','平均回复','总浏览']];
  cats.forEach(c => rows.push([c.name, tag(c), c.count, (c.themes||[]).length, c.total_replies, c.avg_replies, c.total_views]));
  rows.push([]); rows.push(['日期','起点相关帖','AI治理判定']);
  Object.keys(M.daily).forEach(k => rows.push([k, M.daily[k], M.ai_daily[k]]));
  downloadCsv(`lkong_summary_${M.date_range.replace(/[^0-9]/g,'-')}.csv`, rows);
});
document.getElementById('btnProblems').addEventListener('click', () => {
  const rows = [['主题','类别','问题主题','涉及篇数','合计回复','代表帖标题','回复','浏览','发帖日','链接']];
  cats.forEach(c => (c.themes||[]).forEach(t => t.top_posts.forEach(p =>
    rows.push([c.name, tag(c), t.theme, t.count, t.total_replies, p.title, p.replies, p.views, p.date, p.url]))));
  downloadCsv(`lkong_problems_${M.date_range.replace(/[^0-9]/g,'-')}.csv`, rows);
});
document.getElementById('btnPosts').addEventListener('click', () => {
  const rows = [['主题','类别','问题主题','帖子标题','回复','浏览','发帖日','作者','链接']];
  cats.forEach(c => (c.themes||[]).forEach(t => (t.all_posts||t.top_posts).forEach(p =>
    rows.push([c.name, tag(c), t.theme, p.title, p.replies, p.views, p.date, p.author||'', p.url]))));
  downloadCsv(`lkong_posts_${M.date_range.replace(/[^0-9]/g,'-')}.csv`, rows);
});
</script>
</body>
</html>
'''

def make_html_report(data_path, out_path, title, pages="本期抓取", insight="", insight_text="查看本期洞察 →"):
    """生成单文件 HTML 舆情报告"""
    paths = [p.strip() for p in insight.split(",") if p.strip()]
    texts = [t.strip() for t in insight_text.split(",") if t.strip()]
    insight_btn = "".join(
        f'<a class="btn" href="{p}" style="display:inline-block;text-decoration:none;'
        f'background:var(--accent-bg);border-color:var(--accent);font-weight:600;">'
        f'{texts[i] if i < len(texts) else "查看专题 →"}</a>'
        for i, p in enumerate(paths))

    data = json.load(open(data_path, encoding="utf-8"))
    DATA_JSON = json.dumps(data, ensure_ascii=False, indent=1)
    html = (TEMPLATE.replace("__TITLE__", title)
                    .replace("__PAGES__", pages)
                    .replace("__INSIGHT_BTN__", insight_btn)
                    .replace("__REPORT_DATA__", DATA_JSON))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成: {out_path} ({len(html.encode('utf-8'))} 字节)")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="生成 HTML 舆情报告")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--pages", default="本期抓取")
    ap.add_argument("--insight", default="")
    ap.add_argument("--insight-text", default="查看本期洞察 →")
    args = ap.parse_args()
    make_html_report(args.data, args.out, args.title, args.pages, args.insight, args.insight_text)


if __name__ == "__main__":
    main()
