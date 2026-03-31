"""
内容创作 BI 看板 — 每日独立发布15篇文章追踪
支持暗黑模式，数据持久化至本地 data.json
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json, os

# ── 全局常量 ─────────────────────────────────────────────────────────────────
DAILY_TARGET   = 15
PROCESSES      = ["制作图片", "制作封面", "剪辑视频", "写文案", "上传帖子"]
PROCESS_ICONS  = ["🖼️", "🎨", "🎬", "✍️", "📤"]
DATA_FILE      = os.path.join(os.path.dirname(__file__), "data.json")

# Plotly 暗色主题调色板
COLORS = {
    "primary":   "#4F8EF7",
    "success":   "#2ECC71",
    "warning":   "#F39C12",
    "danger":    "#E74C3C",
    "muted":     "#636EFA",
    "process":   ["#4F8EF7","#2ECC71","#F39C12","#9B59B6","#1ABC9C"],
}

# ── 页面配置 ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="内容创作 BI 看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 注入全局 CSS（兼容亮色/暗色主题）
st.markdown("""
<style>
/* 卡片统一样式 */
.kpi-card {
    background: var(--secondary-background-color);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 4px;
    border-left: 5px solid var(--border-color, #4F8EF7);
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.kpi-title  { font-size: 13px; color: #888; margin-bottom: 4px; letter-spacing: .5px; text-transform: uppercase; }
.kpi-value  { font-size: 36px; font-weight: 700; line-height: 1.1; }
.kpi-sub    { font-size: 13px; margin-top: 4px; }

/* 进度条容器 */
.proc-wrap  { margin-bottom: 14px; }
.proc-label { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 4px; }
.proc-bar-bg{ background: #2a2a3a; border-radius: 6px; height: 14px; width: 100%; overflow: hidden; }
.proc-bar-fg{ height: 14px; border-radius: 6px; transition: width .6s ease; }

/* 分割线 */
hr { border-color: rgba(128,128,128,0.2) !important; }
</style>
""", unsafe_allow_html=True)


# ── 数据层 ───────────────────────────────────────────────────────────────────
def _empty_day(total=0):
    return {"total": total, "processes": {p: total for p in PROCESSES}}

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 生成30天示例数据
    today = datetime.today()
    records: dict = {}
    rng = np.random.default_rng(0)
    for i in range(30, 0, -1):
        d   = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        tot = int(rng.integers(7, 17))
        records[d] = {"total": tot, "processes": {p: tot for p in PROCESSES}}
    # 今日真实数据
    records[today.strftime("%Y-%m-%d")] = _empty_day(15)
    _save(records)
    return records

def _save(records: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

records   = load_data()
today_str = datetime.today().strftime("%Y-%m-%d")
today_rec = records.get(today_str, _empty_day())


# ── 侧边栏：数据录入 ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 今日数据录入")
    st.markdown(f"**{today_str}**")
    st.divider()

    new_proc = {}
    for icon, proc in zip(PROCESS_ICONS, PROCESSES):
        new_proc[proc] = st.number_input(
            f"{icon} {proc}",
            min_value=0, max_value=200,
            value=today_rec["processes"].get(proc, 0),
            step=1,
        )
    new_total = st.number_input(
        "📦 今日总发布篇数",
        min_value=0, max_value=200,
        value=today_rec.get("total", 0),
        step=1,
    )
    if st.button("💾 保存今日数据", use_container_width=True, type="primary"):
        records[today_str] = {"total": new_total, "processes": new_proc}
        _save(records)
        st.success("✅ 保存成功！")
        st.rerun()
    st.divider()
    st.caption("数据保存至本地 data.json")


# ── 刷新当日数据 ─────────────────────────────────────────────────────────────
today_rec    = records.get(today_str, _empty_day())
today_total  = today_rec["total"]
today_procs  = today_rec["processes"]
overall_rate = min(today_total / DAILY_TARGET * 100, 100)


# ════════════════════════════════════════════════════════════════════════════
# 主界面
# ════════════════════════════════════════════════════════════════════════════
st.markdown("# 📊 内容创作 BI 看板")
st.markdown(f"<span style='color:#888;font-size:14px'>今日：{today_str} &nbsp;|&nbsp; 每日目标：{DAILY_TARGET} 篇</span>", unsafe_allow_html=True)
st.divider()


# ── Section 1: 顶部 KPI 卡片 ─────────────────────────────────────────────────
st.markdown("### 今日总览")

# 近7天均值（不含今天）
last7_vals = [
    records.get((datetime.today()-timedelta(days=i)).strftime("%Y-%m-%d"), {}).get("total", 0)
    for i in range(1, 8)
]
avg7 = round(float(np.mean(last7_vals)), 1)

# 历史最高
all_totals = [v.get("total", 0) for v in records.values()]
best = max(all_totals) if all_totals else 0

kpi_cols = st.columns(4, gap="medium")

def kpi_card(col, title, value, sub, border_color):
    col.markdown(f"""
    <div class="kpi-card" style="border-left-color:{border_color}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value" style="color:{border_color}">{value}</div>
        <div class="kpi-sub" style="color:#aaa">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(kpi_cols[0], "今日发布总篇数",
         f"{today_total} 篇",
         f"目标 {DAILY_TARGET} 篇 &nbsp;{'✅' if today_total >= DAILY_TARGET else '⏳'}",
         COLORS["primary"])

kpi_card(kpi_cols[1], "整体完成率",
         f"{overall_rate:.0f}%",
         f"{'已达标 🎉' if overall_rate >= 100 else f'还差 {DAILY_TARGET-today_total} 篇'}",
         COLORS["success"] if overall_rate >= 100 else COLORS["warning"])

kpi_card(kpi_cols[2], "近 7 天日均",
         f"{avg7} 篇",
         f"今日 {'↑' if today_total > avg7 else '↓'} {abs(today_total-avg7):.1f} vs 均值",
         COLORS["muted"])

kpi_card(kpi_cols[3], "历史单日最高",
         f"{best} 篇",
         f"{'🏆 今日刷新' if today_total >= best else '继续加油！'}",
         COLORS["warning"])

st.markdown("<br>", unsafe_allow_html=True)


# ── Section 2: 各工序今日完成 + 环形完成率 ──────────────────────────────────
st.markdown("### 今日工序详情")
proc_col, gauge_col = st.columns([1.2, 1], gap="large")

with proc_col:
    st.markdown("**各工序完成数量**")
    for icon, proc, color in zip(PROCESS_ICONS, PROCESSES, COLORS["process"]):
        cnt  = today_procs.get(proc, 0)
        rate = min(cnt / DAILY_TARGET, 1.0)
        pct  = rate * 100
        bar_color = COLORS["success"] if pct >= 100 else (COLORS["warning"] if pct >= 70 else COLORS["danger"])
        st.markdown(f"""
        <div class="proc-wrap">
            <div class="proc-label">
                <span>{icon} <b>{proc}</b></span>
                <span style="color:{bar_color};font-weight:600">{cnt} / {DAILY_TARGET}</span>
            </div>
            <div class="proc-bar-bg">
                <div class="proc-bar-fg" style="width:{pct:.1f}%;background:{bar_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with gauge_col:
    # 仪表盘
    fig_gauge = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = overall_rate,
        number= {"suffix": "%", "font": {"size": 52, "color": COLORS["primary"]}},
        title = {"text": "整体完成率", "font": {"size": 16}},
        gauge = {
            "axis"  : {"range": [0, 100], "tickwidth": 1, "tickcolor": "#666"},
            "bar"   : {"color": COLORS["success"] if overall_rate >= 100 else COLORS["primary"], "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "steps" : [
                {"range": [0,   60], "color": "rgba(231,76,60,0.15)"},
                {"range": [60,  85], "color": "rgba(243,156,18,0.15)"},
                {"range": [85, 100], "color": "rgba(46,204,113,0.15)"},
            ],
            "threshold": {
                "line"     : {"color": "#E74C3C", "width": 3},
                "thickness": 0.75,
                "value"    : 100,
            },
        },
    ))
    fig_gauge.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font={"color": "#ccc"},
        margin=dict(t=50, b=10, l=30, r=30),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# 5工序雷达图
    proc_values = [today_procs.get(p, 0) for p in PROCESSES]
    fig_radar = go.Figure(go.Scatterpolar(
        r     = proc_values + [proc_values[0]],
        theta = PROCESSES + [PROCESSES[0]],
        fill  = "toself",
        fillcolor = "rgba(79,142,247,0.2)",
        line  = dict(color=COLORS["primary"], width=2),
        name  = "今日完成",
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r     = [DAILY_TARGET] * len(PROCESSES) + [DAILY_TARGET],
        theta = PROCESSES + [PROCESSES[0]],
        mode  = "lines",
        line  = dict(color=COLORS["danger"], dash="dash", width=1.5),
        name  = f"目标 {DAILY_TARGET}",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, DAILY_TARGET + 3], color="#888"),
            angularaxis=dict(color="#aaa"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#ccc"},
        legend=dict(font=dict(size=11)),
        height=300,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()


# ── Section 3: 历史趋势（近30天）───────────────────────────────────────────
st.markdown("### 历史发布趋势（近 30 天）")

rows_hist = []
for i in range(29, -1, -1):
    d   = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    tot = records.get(d, {}).get("total", 0)
    rows_hist.append({"日期": d, "发布篇数": tot})
df_hist = pd.DataFrame(rows_hist)
df_hist["日期"] = pd.to_datetime(df_hist["日期"])

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=df_hist["日期"], y=df_hist["发布篇数"],
    mode="lines+markers",
    name="每日发布",
    line=dict(color=COLORS["primary"], width=2.5, shape="spline"),
    marker=dict(size=6, color=COLORS["primary"]),
    fill="tozeroy",
    fillcolor="rgba(79,142,247,0.1)",
))
fig_line.add_hline(
    y=DAILY_TARGET, line_dash="dot", line_color=COLORS["danger"], line_width=1.5,
    annotation_text=f"日目标 {DAILY_TARGET}", annotation_font_color=COLORS["danger"],
    annotation_position="top right",
)
fig_line.add_hline(
    y=avg7, line_dash="dash", line_color=COLORS["warning"], line_width=1.2,
    annotation_text=f"7日均值 {avg7}", annotation_font_color=COLORS["warning"],
    annotation_position="bottom right",
)
fig_line.update_layout(
    height=340,
    xaxis=dict(showgrid=False, title=""),
    yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title="篇数"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font={"color": "#ccc"},
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=30, b=20),
)
st.plotly_chart(fig_line, use_container_width=True)


# ── Section 4: 近7天各工序分组柱状图 ────────────────────────────────────────
st.markdown("### 近 7 天工序完成明细")

rows_proc = []
for i in range(6, -1, -1):
    d        = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    proc_day = records.get(d, {}).get("processes", {p: 0 for p in PROCESSES})
    for proc, cnt in proc_day.items():
        rows_proc.append({"日期": d, "工序": proc, "完成数": cnt})
df_proc = pd.DataFrame(rows_proc)

if not df_proc.empty:
    fig_bar = px.bar(
        df_proc,
        x="日期", y="完成数", color="工序",
        barmode="group",
        color_discrete_sequence=COLORS["process"],
    )
    fig_bar.add_hline(
        y=DAILY_TARGET, line_dash="dot", line_color=COLORS["danger"],
        annotation_text=f"目标 {DAILY_TARGET}", annotation_font_color=COLORS["danger"],
    )
    fig_bar.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font={"color": "#ccc"},
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title="篇数"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


st.divider()
st.caption("📁 数据存储于本地 `data.json` | 侧边栏可随时录入/更新今日数据")
