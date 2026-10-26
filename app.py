# -*- coding: utf-8 -*-
"""
LKong Sentinel - 龙空舆情监控 Gradio 在线 Demo

用法:
  pip install gradio
  python app.py
"""
import json
import os
import sys
import tempfile

try:
    import gradio as gr
except ImportError:
    print("请先安装 gradio: pip install gradio")
    sys.exit(1)

# 将上级目录加入路径以便导入 lkong_sentinel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lkong_sentinel.reporter import make_html_report
from lkong_sentinel.exporter import export_xlsx


def analyze_file(file_obj):
    """上传 JSON 数据文件，生成 HTML 报告和 Excel"""
    if file_obj is None:
        return None, None, "请先上传文件"

    try:
        data = json.load(open(file_obj.name, encoding="utf-8"))
    except Exception as e:
        return None, None, f"文件解析失败: {e}"

    # 基本信息
    meta = data.get("meta", {})
    cats = data.get("categories", [])
    info = f"""
### 数据概览

| 指标 | 数值 |
|------|------|
| 统计区间 | {meta.get('date_range', '-')} |
| 周期内活跃帖 | {meta.get('total_raw_posts', 0)} 篇 |
| 起点相关帖 | {meta.get('gated_total', 0)} 篇 |
| 限定主题 | {len([c for c in cats if not c.get('supplementary')])} 个 |
| 补充类 | {len([c for c in cats if c.get('supplementary')])} 个 |
| 生成时间 | {meta.get('generated_at', '-')} |
"""

    # 主题列表
    theme_info = "### 主题分布\n\n| 主题 | 帖子数 | 总回复 | 问题主题数 |\n|---|---|---|---|\n"
    for c in cats:
        mark = "〔补充〕" if c.get("supplementary") else ""
        theme_info += f"| {mark}{c['name']} | {c['count']} | {c['total_replies']} | {len(c.get('themes', []))} |\n"

    # 生成 HTML 报告
    tmp_dir = tempfile.mkdtemp()
    html_path = os.path.join(tmp_dir, "report.html")
    try:
        make_html_report(file_obj.name, html_path, meta.get("date_range", "报告"))
    except Exception as e:
        html_path = None
        html_err = str(e)

    # 生成 Excel
    xlsx_path = os.path.join(tmp_dir, "report.xlsx")
    try:
        export_xlsx(file_obj.name, xlsx_path)
    except Exception as e:
        xlsx_path = None
        xlsx_err = str(e)

    summary = info + "\n" + theme_info
    return html_path, xlsx_path, summary


# ── Gradio 界面 ──────────────────────────────────────────────
with gr.Blocks(title="LKong Sentinel - 龙空舆情分析", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🕵 LKong Sentinel · 龙空舆情分析 Demo

        上传你的分类 JSON 数据文件，一键生成可视化 HTML 报告和 Excel 工作簿。
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="上传 JSON 数据文件", file_types=[".json"])
            analyze_btn = gr.Button("🚀 开始分析", variant="primary", size="lg")

        with gr.Column(scale=2):
            summary_output = gr.Markdown(label="分析结果")
            with gr.Row():
                html_output = gr.File(label="📊 HTML 报告", visible=True)
                xlsx_output = gr.File(label="📋 Excel 工作簿", visible=True)

    analyze_btn.click(
        fn=analyze_file,
        inputs=[file_input],
        outputs=[html_output, xlsx_output, summary_output],
    )

    gr.Markdown(
        """
        ---
        ### 数据格式说明

        上传的 JSON 应包含以下结构：
        ```json
        {
          "categories": [
            {
              "name": "主题名称",
              "count": 42,
              "total_replies": 1523,
              "total_views": 28000,
              "avg_replies": 362,
              "themes": [...]
            }
          ],
          "meta": {
            "date_range": "2026-10-13 至 2026-10-19",
            "total_raw_posts": 892,
            "gated_total": 186,
            "generated_at": "2026-10-26 18:00"
          }
        }
        ```
        """
    )


if __name__ == "__main__":
    demo.launch(server_port=7860)
