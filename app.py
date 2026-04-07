"""
内容创作 BI 看板 - 最终完整专业版
每日独立发布15篇文章追踪系统
支持自动刷新 + 数据持久化 + CSV 导入/导出
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
import io

# ═══════════════════════════════════════════════════════
# 全局常量
# ═══════════════════════════════════════════════════════
DAILY_TARGET = 15
PROCESSES = ["制作图片", "制作封面", "剪辑视频", "写文案", "上传帖子"]
PROCESS_ICONS = ["🖼️", "🎨", "🎬", "✍", "📤"]

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# 暗黑风格颜色配置
CLR = {
    "bg": "#0e0e0e", "card": "#161616", "border": "#262626",
    "text1": "#f0f0f0", "text2": "#888888", "text3": "#444444",
    "blue": "#4F8EF7", "green": "#2ECC71", "gridline": "rgba(255,255,255,0.06)",
}

# ═══════════════════════════════════════════════════════
# 页面配置与样式
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="内容创作看板", page_icon="📋",
    layout="wide", initial_sidebar_state="expanded",
)

st.markdown(f"""<style>
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {CLR["bg"]}; color: {CLR["text1"]};
}}
[data-testid="stSidebar"] {{ background-color: {CLR["card"]}; }}
.block-container {{ padding-top: 1.2rem; }}
div[data-testid="stFileUploader"] label {{ color: {CLR["text2"]}; font-size: 0.82rem; }}
</style>""", unsafe_allow_html=True)

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
# CSV 导入 / 导出 工具函数
# ═══════════════════════════════════════════════════════
CSV_COLUMNS = ["日期", "总篇数"] + PROCESSES

def records_to_df(records: dict) -> pd.DataFrame:
    """把内部 records dict 转成 DataFrame"""
    rows = []
    for date_str, v in sorted(records.items()):
        row = {"日期": date_str, "总篇数": v.get("total", 0)}
        for p in PROCESSES:
            row[p] = v.get("processes", {}).get(p, 0)
        rows.append(row)
    return pd.DataFrame(rows, columns=CSV_COLUMNS) if rows else pd.DataFrame(columns=CSV_COLUMNS)

def import_csv(uploaded_file) -> tuple[int, list[str]]:
    """
    解析上传的 CSV，合并到 session_state.records。
    返回 (成功行数, 错误信息列表)
    """
    try:
        df = pd.read_csv(uploaded_file, dtype=str)
    except Exception as e:
        return 0, [f"文件读取失败：{e}"]

    df.columns = df.columns.str.strip()
    errors = []
    count = 0

    # 必须有"日期"列
    if "日期" not in df.columns:
        return 0, ["CSV 缺少「日期」列，请检查表头。"]

    for idx, row in df.iterrows():
        line = idx + 2  # 行号（含表头）
        date_str = str(row.get("日期", "")).strip()

        # 校验日期格式
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"第 {line} 行：日期格式错误「{date_str}」，应为 YYYY-MM-DD")
            continue

        # 解析总篇数
        try:
            total = int(float(str(row.get("总篇数", 0)).strip() or 0))
        except ValueError:
            errors.append(f"第 {line} 行：总篇数不是数字「{row.get('总篇数')}」")
            continue

        # 解析各工序
        procs = {}
        for p in PROCESSES:
            raw = str(row.get(p, 0)).strip() if p in df.columns else "0"
            try:
                procs[p] = int(float(raw or 0))
            except ValueError:
                errors.append(f"第 {line} 行：工序「{p}」值不是数字「{raw}」，已置为 0")
                procs[p] = 0

        # 写入（覆盖同日期数据）
        st.session_state.records[date_str] = {"total": total, "processes": procs}
        count += 1

    if count > 0:
        save_data(st.session_state.records)

    return count, errors

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
        "total": 0, "processes": {p: 0 for p in PROCESSES}
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
    st.markdown(f"<div style='color:{CLR['text2']};font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;padding:4px 0 8px'>今日录入</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{CLR['blue']};font-size:0.85rem;margin-bottom:12px'>{today_str}</div>", unsafe_allow_html=True)

    for icon, proc in zip(PROCESS_ICONS, PROCESSES):
        st.markdown(f"<div style='color:{CLR['text2']};font-size:0.8rem;margin-bottom:4px'>{icon} {proc}</div>", unsafe_allow_html=True)
        key = f"input_{proc}"
        c1, c2, c3 = st.columns([1, 2.2, 1])
        with c1:
            if st.button("−", key=f"dec_{proc}", use_container_width=True):
                st.session_state[key] = max(0, st.session_state[key] - 1)
                st.rerun()
        with c2:
            st.markdown(f"<div style='text-align:center;font-size:1.1rem;font-weight:600;color:{CLR['text1']};padding:4px 0'>{st.session_state[key]}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("＋", key=f"inc_{proc}", use_container_width=True):
                st.session_state[key] += 1
                st.rerun()

    st.markdown("<hr style='border-color:#262626;margin:12px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{CLR['text2']};font-size:0.8rem;margin-bottom:4px'>📦 今日总发布篇数</div>", unsafe_allow_html=True)
    st.session_state["input_total"] = st.number_input(
        label="总篇数", label_visibility="collapsed",
        min_value=0, max_value=500,
        value=st.session_state["input_total"], step=1
    )

    if st.button("✅ 保存今日数据", use_container_width=True, type="primary"):
        st.session_state.records[today_str] = {
            "total": st.session_state["input_total"],
            "processes": {p: st.session_state[f"input_{p}"] for p in PROCESSES}
        }
        save_data(st.session_state.records)
        st.success("✅ 数据已保存并持久化")
        st.rerun()

    # ── CSV 导入 ──────────────────────────────────────
    st.markdown("<hr style='border-color:#262626;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{CLR['text2']};font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;padding:4px 0 8px'>📂 导入 CSV</div>", unsafe_allow_html=True)

    with st.expander("查看 CSV 格式说明", expanded=False):
        st.markdown(f"""
<div style='font-size:0.78rem;color:{CLR["text2"]}'>
表头（第一行）必须包含：<br>
<code>日期,总篇数,制作图片,制作封面,剪辑视频,写文案,上传帖子</code><br><br>
• 日期格式：<code>YYYY-MM-DD</code><br>
• 工序列可省略（默认为 0）<br>
• 同日期数据会被覆盖
</div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "选择 CSV 文件", type=["csv"],
        key="csv_uploader", label_visibility="collapsed"
    )

    if uploaded is not None:
        if st.button("📥 确认导入", use_container_width=True):
            count, errors = import_csv(uploaded)
            if count > 0:
                st.success(f"✅ 成功导入 {count} 条记录")
                # 同步今日输入框
                if today_str in st.session_state.records:
                    td = st.session_state.records[today_str]
                    st.session_state["input_total"] = td["total"]
                    for p in PROCESSES:
                        st.session_state[f"input_{p}"] = td["processes"].get(p, 0)
            if errors:
                for e in errors[:5]:
                    st.warning(e)
                if len(errors) > 5:
                    st.warning(f"…还有 {len(errors)-5} 条错误，请检查 CSV 文件")
            if count > 0:
                st.rerun()

    # ── CSV 导出 ──────────────────────────────────────
    st.markdown("<hr style='border-color:#262626;margin:8px 0'>", unsafe_allow_html=True)
    df_export = records_to_df(st.session_state.records)
    csv_bytes = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇️ 导出全部数据为 CSV",
        data=csv_bytes,
        file_name=f"bi_data_{today_str}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ── 系统设置 ──────────────────────────────────────
    st.markdown("<hr style='border-color:#262626;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{CLR['text2']};font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;padding:4px 0 8px'>系统设置</div>", unsafe_allow_html=True)
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
    st.markdown(f"<h2 style='color:{CLR['text1']};margin:0;font-size:1.5rem'>内容创作看板</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='color:{CLR['text2']};font-size:0.82rem;margin-top:4px'>"
        f"{today_str} &nbsp;·&nbsp; 每日目标 {DAILY_TARGET} 篇 &nbsp;·&nbsp; 近30天累计 {last30_total} 篇</div>",
        unsafe_allow_html=True
    )
with col_s:
    now_str = datetime.now().strftime("%H:%M:%S")
    dot_color = CLR["green"] if st.session_state.auto_refresh else CLR["text3"]
    rf_text = "自动刷新 · 每30秒" if st.session_state.auto_refresh else "自动刷新已关闭"
    st.markdown(
        f"""<div style='text-align:right;font-size:0.75rem;color:{CLR["text2"]};padding-top:6px'>
        <span style='color:{dot_color}'>●</span> {rf_text}<br>
        <span style='color:{CLR["text3"]}'>最后更新 {now_str}</span></div>""",
        unsafe_allow_html=True
    )

# Hero 区域
hero_color = CLR["green"] if today_total >= DAILY_TARGET else CLR["blue"]
badge_text = "达标 ✓" if today_total >= DAILY_TARGET else f"还差 {DAILY_TARGET - today_total} 篇"
badge_color = CLR["green"] if today_total >= DAILY_TARGET else CLR["text2"]

st.markdown(f"""
<div style='background:{CLR["card"]};border:1px solid {CLR["border"]};border-radius:12px;
     padding:24px 32px;margin:16px 0;display:flex;align-items:center;gap:32px'>
  <div>
    <div style='color:{CLR["text2"]};font-size:0.78rem;margin-bottom:4px'>今日已发布</div>
    <div style='color:{hero_color};font-size:3rem;font-weight:700;line-height:1'>{today_total}</div>
    <div style='color:{CLR["text3"]};font-size:0.9rem'>/ {DAILY_TARGET}</div>
  </div>
  <div style='flex:1'>
    <div style='background:{CLR["border"]};border-radius:4px;height:6px;margin-bottom:8px'>
      <div style='background:{hero_color};width:{rate:.0f}%;height:6px;border-radius:4px'></div>
    </div>
    <div style='color:{CLR["text2"]};font-size:0.82rem'>
      完成率 {rate:.0f}% &nbsp;·&nbsp; 7日均值 {avg7} 篇 &nbsp;·&nbsp; 历史最高 {best} 篇
      &nbsp;·&nbsp; <span style='color:{badge_color}'>{badge_text}</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# 5个工序卡片
cols = st.columns(5, gap="medium")
for col, icon, proc in zip(cols, PROCESS_ICONS, PROCESSES):
    cnt = today_procs.get(proc, 0)
    pct = min(cnt / DAILY_TARGET * 100, 100)
    color = CLR["green"] if pct >= 100 else (CLR["blue"] if pct >= 70 else CLR["text2"])
    col.markdown(f"""
<div style='background:{CLR["card"]};border:1px solid {CLR["border"]};border-radius:10px;
     padding:16px;text-align:center'>
  <div style='font-size:1.4rem'>{icon}</div>
  <div style='color:{CLR["text2"]};font-size:0.75rem;margin:4px 0'>{proc}</div>
  <div style='color:{color};font-size:1.4rem;font-weight:700'>{cnt}</div>
  <div style='color:{CLR["text3"]};font-size:0.75rem'>/ {DAILY_TARGET}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# 图表区域
chart_l, chart_r = st.columns([1.65, 1], gap="large")

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=CLR["text2"], size=11),
    margin=dict(t=30, b=10, l=10, r=10),
    xaxis=dict(showgrid=False, showline=False, title="", color=CLR["text3"]),
    yaxis=dict(showgrid=True, gridcolor=CLR["gridline"], showline=False, title="", color=CLR["text3"]),
)

# 近30天趋势折线图
with chart_l:
    st.markdown(f"<div style='color:{CLR['text2']};font-size:0.8rem;margin-bottom:8px'>近 30 天发布趋势</div>", unsafe_allow_html=True)
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
        x=df_h["日期"], y=df_h["篇数"], mode="lines+markers",
        line=dict(color=CLR["blue"], width=2.2, shape="spline"),
        marker=dict(size=6, color=dot_colors),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.08)",
        hovertemplate="%{x|%m-%d}　%{y} 篇<extra></extra>"
    ))
    fig_line.add_hline(y=DAILY_TARGET, line_dash="dot", line_color=CLR["border"],
                       line_width=1, annotation_text=str(DAILY_TARGET),
                       annotation_font_color=CLR["text3"])
    fig_line.update_layout(height=280, showlegend=False, **LAYOUT)
    st.plotly_chart(fig_line, use_container_width=True)

# 今日完成率环形图
with chart_r:
    st.markdown(f"<div style='color:{CLR['text2']};font-size:0.8rem;margin-bottom:8px'>今日完成率</div>", unsafe_allow_html=True)
    ring_color = CLR["green"] if rate >= 100 else CLR["blue"]
    fig_ring = go.Figure(go.Pie(
        values=[rate, 100 - rate], hole=0.74,
        marker=dict(colors=[ring_color, CLR["border"]]),
        textinfo="none", hoverinfo="skip", sort=False
    ))
    fig_ring.add_annotation(text=f"<b>{rate:.0f}%</b>", x=0.5, y=0.5,
                             showarrow=False, font=dict(size=38, color=CLR["text1"]))
    fig_ring.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)",
                            showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_ring, use_container_width=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# 近7天工序柱状图
st.markdown(f"<div style='color:{CLR['text2']};font-size:0.8rem;margin-bottom:8px'>近 7 天工序明细</div>", unsafe_allow_html=True)
proc_data = []
for i in range(6, -1, -1):
    d = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    for proc in PROCESSES:
        proc_data.append({
            "日期": d, "工序": proc,
            "完成数": records.get(d, {}).get("processes", {}).get(proc, 0)
        })
df_proc = pd.DataFrame(proc_data)
fig_bar = px.bar(
    df_proc, x="日期", y="完成数", color="工序", barmode="group",
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

st.caption("数据已自动保存至 data.json 文件。可通过侧边栏导入/导出 CSV。")
