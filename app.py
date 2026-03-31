"""
内容创作 BI 看板 - 最终完整专业版
每日独立发布15篇文章追踪系统
支持自动刷新 + 数据持久化
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import json
import os

# ═══════════════════════════════════════════════════════
# 全局常量
# ═══════════════════════════════════════════════════════
DAILY_TARGET = 15
PROCESSES = ["制作图片", "制作封面", "剪辑视频", "写文案", "上传帖子"]
PROCESS_ICONS = ["🖼️", "🎨", "🎬", "✍", "📤"]

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# 暗黑风格颜色配置
CLR = {
    "bg": "#0e0e0e",
    "card": "#161616",
    "border": "#262626",
    "text1": "#f0f0f0",
    "text2": "#888888",
    "text3": "#444444",
    "blue": "#4F8EF7",
    "green": "#2ECC71",
    "gridline": "rgba(255,255,255,0.06)",
}

# ═══════════════════════════════════════════════════════
# 页面配置与样式
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="内容创作看板",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {CLR['bg']} !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background-color: {CLR['card']};
        padding: 1.8rem 1.4rem;
        border-right: 1px solid {CLR['border']};
    }}
    #MainMenu, footer {{ visibility: hidden; }}
    [data-testid="stDecoration"] {{ display: none; }}
    
    .page-title {{ font-size: 26px; font-weight: 700; letter-spacing: -0.4px; color: {CLR['text1']}; }}
    .page-sub {{ font-size: 13px; color: {CLR['text2']}; margin-top: 4px; }}
    
    .hero {{
        padding: 40px 0 32px;
        text-align: center;
        border-bottom: 1px solid {CLR['border']};
        margin-bottom: 32px;
    }}
    .hero-label {{ font-size: 12px; letter-spacing: 2.5px; text-transform: uppercase; color: {CLR['text2']}; margin-bottom: 8px; }}
    .hero-num {{ font-size: 78px; font-weight: 800; line-height: 1; letter-spacing: -3px; }}
    .hero-denom {{ font-size: 34px; font-weight: 300; color: {CLR['text2']}; }}
    .hero-sub {{ font-size: 13px; color: {CLR['text2']}; margin-top: 14px; letter-spacing: .4px; }}
    
    .pbar-track {{ background: {CLR['border']}; border-radius: 6px; height: 8px; max-width: 380px; margin: 18px auto 0; }}
    .pbar-fill {{ height: 8px; border-radius: 6px; transition: width .6s ease; }}
    
    .proc-card {{
        background: {CLR['card']};
        border: 1px solid {CLR['border']};
        border-radius: 14px;
        padding: 22px 18px 18px;
        text-align: center;
        height: 100%;
    }}
    .proc-icon {{ font-size: 22px; margin-bottom: 10px; }}
    .proc-name {{ font-size: 12px; color: {CLR['text2']}; margin-bottom: 12px; letter-spacing: .4px; }}
    .proc-num {{ font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 6px; }}
    .proc-den {{ font-size: 12px; color: {CLR['text2']}; }}
    .mini-track {{ background: {CLR['border']}; border-radius: 4px; height: 5px; margin-top: 12px; }}
    .mini-fill {{ height: 5px; border-radius: 4px; transition: width .5s; }}
    
    .sb-section {{ 
        font-size: 11.5px; 
        color: {CLR['text2']}; 
        letter-spacing: 1.3px; 
        text-transform: uppercase; 
        margin: 6px 0 14px 0; 
    }}
    .big-num-display {{
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        line-height: 1.1;
        color: {CLR['text1']};
    }}
    .chart-title {{
        font-size: 13.5px; 
        font-weight: 600;
        color: {CLR['text2']};
        letter-spacing: .6px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    .thin-hr {{ border: none; border-top: 1px solid {CLR['border']}; margin: 28px 0; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 数据持久化
# ═══════════════════════════════════════════════════════
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "records" not in st.session_state:
    st.session_state.records = load_data()

# ═══════════════════════════════════════════════════════
# 自动刷新
# ═══════════════════════════════════════════════════════
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

if st.session_state.auto_refresh:
    st_autorefresh(interval=30000, key="autorefresh_key")

# ═══════════════════════════════════════════════════════
# 初始化今日数据
# ═══════════════════════════════════════════════════════
today_str = datetime.today().strftime("%Y-%m-%d")

if today_str not in st.session_state.records:
    st.session_state.records[today_str] = {
        "total": 0,
        "processes": {p: 0 for p in PROCESSES}
    }

for proc in PROCESSES:
    key = f"input_{proc}"
    if key not in st.session_state:
        st.session_state[key] = st.session_state.records[today_str]["processes"].get(proc, 0)

if "input_total" not in st.session_state:
    st.session_state["input_total"] = st.session_state.records[today_str]["total"]

# ═══════════════════════════════════════════════════════
# 侧边栏
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='sb-section'>今日录入</div>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:12.5px;color:{CLR['text2']}'>{today_str}</span>", unsafe_allow_html=True)
    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)

    for icon, proc in zip(PROCESS_ICONS, PROCESSES):
        st.markdown(f"<div style='font-size:12.5px;color:{CLR['text2']};margin-bottom:6px'>{icon} {proc}</div>", unsafe_allow_html=True)
        key = f"input_{proc}"
        c1, c2, c3 = st.columns([1, 2.2, 1])
        with c1:
            if st.button("−", key=f"dec_{proc}", use_container_width=True):
                st.session_state[key] = max(0, st.session_state[key] - 1)
                st.rerun()
        with c2:
            st.markdown(f"<div class='big-num-display'>{st.session_state[key]}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("＋", key=f"inc_{proc}", use_container_width=True):
                st.session_state[key] += 1
                st.rerun()

    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12.5px;color:{CLR['text2']};margin-bottom:6px'>📦 今日总发布篇数</div>", unsafe_allow_html=True)
    
    st.session_state["input_total"] = st.number_input(
        label="总篇数", label_visibility="collapsed",
        min_value=0, max_value=500, value=st.session_state["input_total"], step=1
    )

    if st.button("✅ 保存今日数据", use_container_width=True, type="primary"):
        st.session_state.records[today_str] = {
            "total": st.session_state["input_total"],
            "processes": {p: st.session_state[f"input_{p}"] for p in PROCESSES}
        }
        save_data(st.session_state.records)
        st.success("✅ 数据已保存并持久化")
        st.rerun()

    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)
    st.markdown("<div class='sb-section'>系统设置</div>", unsafe_allow_html=True)
    
    auto_on = st.toggle("自动刷新（每 30 秒）", value=st.session_state.auto_refresh)
    if auto_on != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_on
        st.rerun()

    if st.button("💾 手动保存数据", use_container_width=True):
        save_data(st.session_state.records)
        st.success("数据已手动保存")

# ═══════════════════════════════════════════════════════
# 计算指标
# ═══════════════════════════════════════════════════════
records = st.session_state.records
today_total = records.get(today_str, {}).get("total", 0)
today_procs = records.get(today_str, {}).get("processes", {p: 0 for p in PROCESSES})

rate = min(today_total / DAILY_TARGET * 100, 100)

last7 = [records.get((datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d"), {}).get("total", 0) for i in range(1, 8)]
avg7 = round(float(np.mean(last7)), 1) if last7 else 0

best = max((v.get("total", 0) for v in records.values()), default=0)
last30_total = sum(v.get("total", 0) for v in records.values())

# ═══════════════════════════════════════════════════════
# 主界面
# ═══════════════════════════════════════════════════════
col_t, col_s = st.columns([3.5, 1])
with col_t:
    st.markdown(f"<div class='page-title'>内容创作看板</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-sub'>{today_str} &nbsp;·&nbsp; 每日目标 {DAILY_TARGET} 篇 &nbsp;·&nbsp; 近30天累计 {last30_total} 篇</div>",
        unsafe_allow_html=True
    )

with col_s:
    now_str = datetime.now().strftime("%H:%M:%S")
    dot_color = CLR["green"] if st.session_state.auto_refresh else CLR["text3"]
    rf_text = "自动刷新 · 每30秒" if st.session_state.auto_refresh else "自动刷新已关闭"
    st.markdown(
        f"""
        <div style='text-align:right;padding-top:12px'>
            <span style='display:inline-block;width:8px;height:8px;background:{dot_color};border-radius:50%;margin-right:6px;'></span>
            <span style='font-size:12px;color:{CLR['text2']}'>{rf_text}</span><br>
            <span style='font-size:11.5px;color:{CLR['text3']}'>最后更新 {now_str}</span>
        </div>
        """, unsafe_allow_html=True
    )

# Hero 区域
hero_color = CLR["green"] if today_total >= DAILY_TARGET else CLR["blue"]
badge_text = "达标 ✓" if today_total >= DAILY_TARGET else f"还差 {DAILY_TARGET - today_total} 篇"
badge_color = CLR["green"] if today_total >= DAILY_TARGET else CLR["text2"]

st.markdown(f"""
<div class="hero">
    <div class="hero-label">今日已发布</div>
    <div class="hero-num" style="color:{hero_color}">{today_total}<span class="hero-denom"> / {DAILY_TARGET}</span></div>
    <div class="hero-sub">
        完成率 <b style="color:{hero_color}">{rate:.0f}%</b>
        &nbsp;·&nbsp; 7日均值 {avg7} 篇
        &nbsp;·&nbsp; 历史最高 {best} 篇
        &nbsp;·&nbsp; <span style="color:{badge_color}">{badge_text}</span>
    </div>
    <div class="pbar-track">
        <div class="pbar-fill" style="width:{rate:.1f}%; background:{hero_color};"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5个工序卡片
cols = st.columns(5, gap="medium")
for col, icon, proc in zip(cols, PROCESS_ICONS, PROCESSES):
    cnt = today_procs.get(proc, 0)
    pct = min(cnt / DAILY_TARGET * 100, 100)
    color = CLR["green"] if pct >= 100 else (CLR["blue"] if pct >= 70 else CLR["text2"])
    
    col.markdown(f"""
    <div class="proc-card">
        <div class="proc-icon">{icon}</div>
        <div class="proc-name">{proc}</div>
        <div class="proc-num" style="color:{color}">{cnt}</div>
        <div class="proc-den">/ {DAILY_TARGET}</div>
        <div class="mini-track">
            <div class="mini-fill" style="width:{pct:.0f}%; background:{color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='thin-hr'></div>", unsafe_allow_html=True)

# 图表区域
chart_l, chart_r = st.columns([1.65, 1], gap="large")

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=CLR["text2"], size=11),
    margin=dict(t=30, b=10, l=10, r=10),
    xaxis=dict(showgrid=False, showline=False, title="", color=CLR["text3"]),
    yaxis=dict(showgrid=True, gridcolor=CLR["gridline"], showline=False, title="", color=CLR["text3"]),
)

# 近30天趋势折线图
with chart_l:
    st.markdown("<div class='chart-title'>近 30 天发布趋势</div>", unsafe_allow_html=True)
    hist_data = []
    for i in range(29, -1, -1):
        d = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        val = records.get(d, {}).get("total", 0)
        hist_data.append({"日期": d, "篇数": val})
    
    df_h = pd.DataFrame(hist_data)
    df_h["日期"] = pd.to_datetime(df_h["日期"])
    dot_colors = [CLR["green"] if v >= DAILY_TARGET else CLR["text3"] for v in df_h["篇数"]]

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_h["日期"], y=df_h["篇数"],
        mode="lines+markers",
        line=dict(color=CLR["blue"], width=2.2, shape="spline"),
        marker=dict(size=6, color=dot_colors),
        fill="tozeroy",
        fillcolor="rgba(79,142,247,0.08)",
        hovertemplate="%{x|%m-%d}　%{y} 篇<extra></extra>"
    ))
    fig_line.add_hline(y=DAILY_TARGET, line_dash="dot", line_color=CLR["border"], line_width=1,
                       annotation_text=str(DAILY_TARGET), annotation_font_color=CLR["text3"])
    fig_line.update_layout(height=280, showlegend=False, **LAYOUT)
    st.plotly_chart(fig_line, use_container_width=True)

# 今日完成率环形图
with chart_r:
    st.markdown("<div class='chart-title'>今日完成率</div>", unsafe_allow_html=True)
    ring_color = CLR["green"] if rate >= 100 else CLR["blue"]
    fig_ring = go.Figure(go.Pie(
        values=[rate, 100 - rate],
        hole=0.74,
        marker=dict(colors=[ring_color, CLR["border"]]),
        textinfo="none",
        hoverinfo="skip",
        sort=False
    ))
    fig_ring.add_annotation(text=f"<b>{rate:.0f}%</b>", x=0.5, y=0.5, showarrow=False,
                            font=dict(size=38, color=CLR["text1"]))
    fig_ring.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                           margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_ring, use_container_width=True)

st.markdown("<div class='thin-hr'></div>", unsafe_allow_html=True)

# 近7天工序柱状图
st.markdown("<div class='chart-title'>近 7 天工序明细</div>", unsafe_allow_html=True)

proc_data = []
for i in range(6, -1, -1):
    d = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    for proc in PROCESSES:
        proc_data.append({
            "日期": d,
            "工序": proc,
            "完成数": records.get(d, {}).get("processes", {}).get(proc, 0)
        })

df_proc = pd.DataFrame(proc_data)
fig_bar = px.bar(
    df_proc, x="日期", y="完成数", color="工序",
    barmode="group",
    color_discrete_sequence=[CLR["blue"], "#3a7bd5", CLR["green"], "#27ae60", "#888888"]
)
fig_bar.add_hline(y=DAILY_TARGET, line_dash="dot", line_color=CLR["border"])
fig_bar.update_layout(
    height=310,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=10, color=CLR["text2"]), bgcolor="rgba(0,0,0,0)"),
    **LAYOUT
)
st.plotly_chart(fig_bar, use_container_width=True)

st.caption("数据已自动保存至 data.json 文件。如需备份，请从侧边栏下载或在 GitHub 下载仓库。")
