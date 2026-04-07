    "gridline": "rgba(255,255,255,0.05)",
}

# ═══════════════════════════════════════════════════════
# 页面配置
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="内容创作看板",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
/* 全局背景 */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stToolbar"] {{
    background-color: {CLR['bg']} !important;
}}
section.main > div {{ padding-top: 1.6rem; padding-bottom: 2rem; }}
[data-testid="stSidebar"] > div:first-child {{
    background-color: {CLR['card']};
    padding: 1.8rem 1.4rem;
    border-right: 1px solid {CLR['border']};
}}

/* 隐藏默认装饰 */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}

/* 全局文字色 */
html, body, p, div, span, label {{ color: {CLR['text1']}; }}

/* 大标题行 */
.topbar {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 20px;
}}
.page-title {{ font-size: 24px; font-weight: 700; letter-spacing: -0.3px; color: {CLR['text1']}; }}
.page-sub   {{ font-size: 12px; color: {CLR['text2']}; margin-top: 3px; }}

/* Hero 区 */
.hero {{
    padding: 36px 0 28px;
    text-align: center;
    border-bottom: 1px solid {CLR['border']};
    margin-bottom: 28px;
}}
.hero-label {{ font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: {CLR['text2']}; margin-bottom: 10px; }}
.hero-num   {{ font-size: 72px; font-weight: 800; line-height: 1; letter-spacing: -2px; }}
.hero-denom {{ font-size: 32px; font-weight: 300; color: {CLR['text2']}; }}
.hero-sub   {{ font-size: 12px; color: {CLR['text2']}; margin-top: 12px; letter-spacing: .3px; }}

/* 完成率进度条 */
.pbar-wrap  {{ margin: 16px auto 0; max-width: 360px; }}
.pbar-meta  {{ display: flex; justify-content: space-between;
               font-size: 11px; color: {CLR['text2']}; margin-bottom: 6px; }}
.pbar-track {{ background: {CLR['border']}; border-radius: 4px; height: 6px; }}
.pbar-fill  {{ height: 6px; border-radius: 4px; transition: width .5s; }}

/* 工序卡片 */
.proc-card {{
    background: {CLR['card']};
    border: 1px solid {CLR['border']};
    border-radius: 12px;
    padding: 20px 16px 16px;
    text-align: center;
}}
.proc-icon  {{ font-size: 20px; margin-bottom: 8px; }}
.proc-name  {{ font-size: 11px; color: {CLR['text2']}; margin-bottom: 12px; letter-spacing: .3px; }}
.proc-num   {{ font-size: 34px; font-weight: 700; line-height: 1; margin-bottom: 4px; }}
.proc-den   {{ font-size: 11px; color: {CLR['text2']}; margin-bottom: 10px; }}
.mini-track {{ background: {CLR['border']}; border-radius: 3px; height: 4px; }}
.mini-fill  {{ height: 4px; border-radius: 3px; }}

/* 侧边栏 */
.sb-section {{ font-size: 11px; color: {CLR['text2']};
               letter-spacing: 1.2px; text-transform: uppercase;
               margin-bottom: 12px; margin-top: 4px; }}
.proc-input-row {{ margin-bottom: 18px; }}
.proc-input-label {{ font-size: 12px; color: {CLR['text2']}; margin-bottom: 6px; }}
.big-num-display {{
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    line-height: 1.2;
    color: {CLR['text1']};
    padding: 2px 0;
}}

/* 自动刷新状态点 */
.rf-dot {{
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}}

/* 细分割线 */
.thin-hr {{ border: none; border-top: 1px solid {CLR['border']}; margin: 20px 0; }}

/* 图表区标题 */
.chart-title {{
    font-size: 13px; font-weight: 600;
    color: {CLR['text2']};
    letter-spacing: .5px;
    text-transform: uppercase;
    margin-bottom: 2px;
}}

/* 按钮覆盖 */
[data-testid="stButton"] button {{
    background: {CLR['card']};
    color: {CLR['text1']};
    border: 1px solid {CLR['border']};
    border-radius: 8px;
    font-size: 18px;
    font-weight: 700;
    padding: 2px 0;
}}
[data-testid="stButton"] button:hover {{
    border-color: {CLR['blue']};
    color: {CLR['blue']};
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# 自动刷新（顶部，条件执行）
# ═══════════════════════════════════════════════════════
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

if st.session_state.auto_refresh:
    st_autorefresh(interval=30_000, key="autorefresh_ticker")


# ═══════════════════════════════════════════════════════
# 数据层
# ═══════════════════════════════════════════════════════
def _seed() -> dict:
    today = datetime.today()
    rng   = np.random.default_rng(42)
    rec   = {}
    for i in range(30, 0, -1):
        d   = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        tot = int(rng.integers(8, 17))
        rec[d] = {"total": tot, "processes": {p: tot for p in PROCESSES}}
    rec[today.strftime("%Y-%m-%d")] = {
        "total": 15,
        "processes": {p: 15 for p in PROCESSES},
    }
    return rec

if "records" not in st.session_state:
    st.session_state.records = _seed()

today_str = datetime.today().strftime("%Y-%m-%d")
_saved    = st.session_state.records.get(today_str, {})

# 初始化输入值
for proc in PROCESSES:
    key = f"input_{proc}"
    if key not in st.session_state:
        st.session_state[key] = _saved.get("processes", {}).get(proc, 0)
if "input_total" not in st.session_state:
    st.session_state["input_total"] = _saved.get("total", 0)


# ═══════════════════════════════════════════════════════
# 侧边栏
# ═══════════════════════════════════════════════════════
with st.sidebar:
    # 标题
    st.markdown(f"<div class='sb-section'>今日录入</div>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:12px;color:{CLR['text2']}'>{today_str}</span>", unsafe_allow_html=True)
    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)

    # 5 道工序：− 数字 ＋
    for icon, proc in zip(P_ICONS, PROCESSES):
        st.markdown(
            f"<div class='proc-input-label'>{icon}&nbsp; {proc}</div>",
            unsafe_allow_html=True,
        )
        key = f"input_{proc}"
        c_l, c_m, c_r = st.columns([1, 2, 1])
        with c_l:
            if st.button("−", key=f"dec_{proc}", use_container_width=True):
                st.session_state[key] = max(0, st.session_state[key] - 1)
                st.rerun()
        with c_m:
            st.markdown(
                f"<div class='big-num-display'>{st.session_state[key]}</div>",
                unsafe_allow_html=True,
            )
        with c_r:
            if st.button("＋", key=f"inc_{proc}", use_container_width=True):
                st.session_state[key] = st.session_state[key] + 1
                st.rerun()

    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)

    # 总篇数
    st.markdown(
        f"<div class='proc-input-label'>📦&nbsp; 今日总发布篇数</div>",
        unsafe_allow_html=True,
    )
    st.session_state["input_total"] = st.number_input(
        label="总篇数",
        label_visibility="collapsed",
        min_value=0, max_value=500,
        value=st.session_state["input_total"],
        step=1,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 保存
    if st.button("✅  保存今日数据", use_container_width=True, type="primary"):
        st.session_state.records[today_str] = {
            "total": st.session_state["input_total"],
            "processes": {p: st.session_state[f"input_{p}"] for p in PROCESSES},
        }
        st.success("已保存！")
        st.rerun()

    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)

    # 自动刷新开关（侧边栏底部）
    st.markdown(f"<div class='sb-section'>系统设置</div>", unsafe_allow_html=True)
    auto_on = st.toggle(
        "自动刷新（每 30 秒）",
        value=st.session_state.auto_refresh,
        key="auto_refresh_toggle",
    )
    if auto_on != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_on
        st.rerun()

    st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)

    # 备份
    st.markdown(f"<div class='sb-section'>数据备份</div>", unsafe_allow_html=True)
    st.download_button(
        "⬇️ 导出 JSON",
        data=json.dumps(st.session_state.records, ensure_ascii=False, indent=2).encode(),
        file_name=f"bi_{today_str}.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded = st.file_uploader("导入 JSON", type="json", label_visibility="collapsed")
    if uploaded:
        try:
            st.session_state.records = json.load(io.TextIOWrapper(uploaded, encoding="utf-8"))
            st.success("数据已载入！")
            st.rerun()
        except Exception as e:
            st.error(f"格式错误：{e}")


# ═══════════════════════════════════════════════════════
# 计算指标
# ═══════════════════════════════════════════════════════
records     = st.session_state.records
today_total = records.get(today_str, {}).get("total", 0)
today_procs = records.get(today_str, {}).get("processes", {p: 0 for p in PROCESSES})
rate        = min(today_total / DAILY_TARGET * 100, 100)

last7 = [
    records.get((datetime.today()-timedelta(days=i)).strftime("%Y-%m-%d"), {}).get("total", 0)
    for i in range(1, 8)
]
avg7   = round(float(np.mean(last7)), 1)
best   = max((v.get("total", 0) for v in records.values()), default=0)
last30 = sum(
    records.get((datetime.today()-timedelta(days=i)).strftime("%Y-%m-%d"), {}).get("total", 0)
    for i in range(0, 30)
)


# ═══════════════════════════════════════════════════════
# 主界面
# ═══════════════════════════════════════════════════════

# ── 顶部标题行（含自动刷新状态）────────────────────────
now_str    = datetime.now().strftime("%H:%M:%S")
dot_color  = CLR["green"] if st.session_state.auto_refresh else CLR["text3"]
rf_label   = f"自动刷新 · 每30秒" if st.session_state.auto_refresh else "自动刷新已关闭"

title_col, status_col = st.columns([3, 1])
with title_col:
    st.markdown(
        f"<div class='page-title'>内容创作看板</div>"
        f"<div class='page-sub'>{today_str} &nbsp;·&nbsp; 目标 {DAILY_TARGET} 篇 &nbsp;·&nbsp; 近30天累计 {last30} 篇</div>",
        unsafe_allow_html=True,
    )
with status_col:
    st.markdown(
        f"<div style='text-align:right;padding-top:4px'>"
        f"<span class='rf-dot' style='background:{dot_color}'></span>"
        f"<span style='font-size:11px;color:{CLR['text2']}'>{rf_label}</span><br>"
        f"<span style='font-size:11px;color:{CLR['text3']}'>最后更新 {now_str}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Hero：今日已发布 ──────────────────────────────────
hero_color  = CLR["green"] if today_total >= DAILY_TARGET else CLR["blue"]
pbar_color  = CLR["green"] if today_total >= DAILY_TARGET else CLR["blue"]
badge_text  = "达标 ✓" if today_total >= DAILY_TARGET else f"还差 {DAILY_TARGET - today_total} 篇"
badge_color = CLR["green"] if today_total >= DAILY_TARGET else CLR["text2"]

st.markdown(f"""
<div class="hero">
    <div class="hero-label">今日已发布</div>
    <div class="hero-num" style="color:{hero_color}">
        {today_total}<span class="hero-denom"> / {DAILY_TARGET}</span>
    </div>
    <div class="hero-sub">
        完成率 <b style="color:{hero_color}">{rate:.0f}%</b>
        &nbsp;·&nbsp; 7日均值 {avg7} 篇
        &nbsp;·&nbsp; 历史最高 {best} 篇
        &nbsp;·&nbsp; <span style="color:{badge_color}">{badge_text}</span>
    </div>
    <div class="pbar-wrap">
        <div class="pbar-meta">
            <span>完成率</span><span>{rate:.0f}%</span>
        </div>
        <div class="pbar-track">
            <div class="pbar-fill" style="width:{rate:.1f}%;background:{pbar_color};"></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── 5 工序卡片 ────────────────────────────────────────
cols = st.columns(5, gap="small")
for col, icon, proc in zip(cols, P_ICONS, PROCESSES):
    cnt   = today_procs.get(proc, 0)
    pct   = min(cnt / DAILY_TARGET * 100, 100)
    ncol  = CLR["green"] if pct >= 100 else (CLR["blue"] if pct >= 70 else CLR["text2"])
    bcol  = CLR["green"] if pct >= 100 else (CLR["blue"] if pct >= 70 else CLR["border"])
    col.markdown(f"""
    <div class="proc-card">
        <div class="proc-icon">{icon}</div>
        <div class="proc-name">{proc}</div>
        <div class="proc-num" style="color:{ncol}">{cnt}</div>
        <div class="proc-den">/ {DAILY_TARGET}</div>
        <div class="mini-track">
            <div class="mini-fill" style="width:{pct:.0f}%;background:{bcol};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='thin-hr'></div>", unsafe_allow_html=True)


# ── 图表区（两列）────────────────────────────────────
chart_l, chart_r = st.columns([1.6, 1], gap="medium")

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=CLR["text2"], size=11),
    margin=dict(t=28, b=8, l=8, r=8),
    xaxis=dict(showgrid=False, showline=False, title="", color=CLR["text3"]),
    yaxis=dict(showgrid=True, gridcolor=CLR["gridline"], showline=False, title="", color=CLR["text3"]),
)

# 折线图：近30天趋势
with chart_l:
    st.markdown(f"<div class='chart-title'>近 30 天发布趋势</div>", unsafe_allow_html=True)

    hist = [
        {
            "日期": (datetime.today()-timedelta(days=i)).strftime("%Y-%m-%d"),
            "篇数": records.get(
                (datetime.today()-timedelta(days=i)).strftime("%Y-%m-%d"), {}
            ).get("total", 0),
        }
        for i in range(29, -1, -1)
    ]
    df_h = pd.DataFrame(hist)
    df_h["日期"] = pd.to_datetime(df_h["日期"])
    dot_c = [CLR["green"] if v >= DAILY_TARGET else CLR["text3"] for v in df_h["篇数"]]

    fig_l = go.Figure()
    fig_l.add_trace(go.Scatter(
        x=df_h["日期"], y=df_h["篇数"],
        mode="lines+markers",
        line=dict(color=CLR["blue"], width=1.8, shape="spline"),
        marker=dict(size=5, color=dot_c, line=dict(width=0)),
        fill="tozeroy",
        fillcolor="rgba(79,142,247,0.05)",
        hovertemplate="%{x|%m-%d}　%{y} 篇<extra></extra>",
    ))
    fig_l.add_hline(
        y=DAILY_TARGET,
        line_dash="dot", line_color=CLR["border"], line_width=1,
        annotation_text=f"{DAILY_TARGET}",
        annotation_font_color=CLR["text3"],
        annotation_position="top right",
    )
    fig_l.update_layout(height=240, showlegend=False, **LAYOUT_BASE)
    st.plotly_chart(fig_l, use_container_width=True)

# 完成率环形图（今日）
with chart_r:
    st.markdown(f"<div class='chart-title'>今日完成率</div>", unsafe_allow_html=True)

    ring_color = CLR["green"] if rate >= 100 else CLR["blue"]
    fig_d = go.Figure(go.Pie(
        values=[rate, max(100 - rate, 0)],
        hole=0.72,
        marker=dict(colors=[ring_color, CLR["border"]], line=dict(width=0)),
        textinfo="none",
        hoverinfo="skip",
        sort=False,
    ))
    fig_d.add_annotation(
        text=f"<b>{rate:.0f}%</b>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=32, color=CLR["text1"]),
    )
    fig_d.update_layout(
        height=240,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=16, b=16, l=16, r=16),
    )
    st.plotly_chart(fig_d, use_container_width=True)

st.markdown("<div class='thin-hr'></div>", unsafe_allow_html=True)


# 近7天工序柱状图
st.markdown(f"<div class='chart-title'>近 7 天工序明细</div>", unsafe_allow_html=True)

proc_rows = []
for i in range(6, -1, -1):
    d = (datetime.today()-timedelta(days=i)).strftime("%Y-%m-%d")
    for proc in PROCESSES:
        proc_rows.append({
            "日期": d,
            "工序": proc,
            "完成数": records.get(d, {}).get("processes", {}).get(proc, 0),
        })
df_p = pd.DataFrame(proc_rows)

fig_b = px.bar(
    df_p, x="日期", y="完成数", color="工序",
    barmode="group",
    color_discrete_sequence=[CLR["blue"], "#3a7bd5", CLR["green"], "#27ae60", "#888888"],
)
fig_b.add_hline(
    y=DAILY_TARGET,
    line_dash="dot", line_color=CLR["border"], line_width=1,
    annotation_text=f"{DAILY_TARGET}",
    annotation_font_color=CLR["text3"],
)
fig_b.update_layout(
    height=260,
    showlegend=True,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.01,
        xanchor="right", x=1,
        font=dict(size=10, color=CLR["text2"]),
        bgcolor="rgba(0,0,0,0)",
    ),
    **LAYOUT_BASE,
)
st.plotly_chart(fig_b, use_container_width=True)

st.markdown(
    f"<div style='font-size:11px;color:{CLR['text3']};padding-top:8px'>"
    f"导出 JSON 备份后，下次进入前先从侧边栏导入即可恢复历史数据。"
    f"</div>",
    unsafe_allow_html=True,
)
