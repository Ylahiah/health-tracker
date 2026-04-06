from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go


def inject_global_style() -> None:
    css = """
    <style>
      :root {
        --bg0: #0b0f19;
        --bg1: #0f172a;
        --card: rgba(255,255,255,0.06);
        --card2: rgba(255,255,255,0.09);
        --border: rgba(255,255,255,0.10);
        --text: rgba(255,255,255,0.92);
        --muted: rgba(255,255,255,0.65);
        --accent: #ff4b4b;
        --accent2: #38bdf8;
        --ok: #22c55e;
        --warn: #f59e0b;
        --bad: #ef4444;
        --radius: 22px;
      }

      .stApp {
        background: radial-gradient(1200px 600px at 20% 0%, rgba(56,189,248,0.18), transparent 60%),
                    radial-gradient(900px 520px at 90% 10%, rgba(255,75,75,0.16), transparent 60%),
                    linear-gradient(180deg, var(--bg0), var(--bg1));
        color: var(--text);
      }

      section.main > div.block-container {
        padding-top: 1.25rem;
        padding-bottom: 4.5rem;
        max-width: 1040px;
      }

      @media (max-width: 900px) {
        section.main > div.block-container {
          max-width: 520px;
          padding-left: 1rem;
          padding-right: 1rem;
        }
      }

      .ht-title {
        font-size: 2.2rem;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0.2rem 0 0.75rem 0;
      }

      .ht-subtitle {
        color: var(--muted);
        font-size: 1rem;
        margin-top: -0.25rem;
        margin-bottom: 1rem;
      }

      .ht-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 1rem;
        box-shadow: 0 16px 38px rgba(0,0,0,0.35);
      }

      .ht-card-soft {
        background: linear-gradient(180deg, var(--card2), var(--card));
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 1rem;
        box-shadow: 0 16px 38px rgba(0,0,0,0.35);
      }

      .ht-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
      }

      @media (max-width: 900px) {
        .ht-kpi-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }

      .ht-kpi {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
        padding: 0.85rem 0.85rem;
      }

      .ht-kpi-label {
        color: var(--muted);
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
      }

      .ht-kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
      }

      .ht-kpi-sub {
        color: var(--muted);
        font-size: 0.85rem;
      }

      .ht-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.05);
        color: var(--muted);
        font-size: 0.85rem;
        white-space: nowrap;
      }

      .ht-pill.ok { border-color: rgba(34,197,94,0.35); color: rgba(222,255,236,0.88); background: rgba(34,197,94,0.12); }
      .ht-pill.warn { border-color: rgba(245,158,11,0.35); color: rgba(255,244,222,0.88); background: rgba(245,158,11,0.12); }
      .ht-pill.bad { border-color: rgba(239,68,68,0.35); color: rgba(255,228,228,0.90); background: rgba(239,68,68,0.12); }
      .ht-pill.blue { border-color: rgba(56,189,248,0.35); color: rgba(219,245,255,0.90); background: rgba(56,189,248,0.12); }

      .ht-section-title {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0.25rem 0 0.6rem 0;
      }

      .ht-divider {
        height: 1px;
        background: rgba(255,255,255,0.08);
        margin: 1rem 0;
        border: 0;
      }

      .stButton > button {
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        background: rgba(255,255,255,0.06) !important;
        color: rgba(255,255,255,0.92) !important;
        padding: 0.70rem 0.95rem !important;
        font-weight: 700 !important;
      }

      .stButton > button:hover {
        border-color: rgba(255,255,255,0.22) !important;
        background: rgba(255,255,255,0.09) !important;
      }

      .ht-cta > button {
        background: linear-gradient(90deg, rgba(255,75,75,0.95), rgba(255,75,75,0.78)) !important;
        border: 1px solid rgba(255,75,75,0.45) !important;
      }

      .ht-phone {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 30px;
        padding: 0.9rem;
        box-shadow: 0 18px 44px rgba(0,0,0,0.40);
      }

      .ht-phone-inner {
        background: rgba(255,255,255,0.95);
        border-radius: 26px;
        padding: 0.9rem 0.9rem 1.1rem 0.9rem;
        color: rgba(0,0,0,0.86);
        position: relative;
        overflow: hidden;
      }

      .ht-phone-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
        margin-bottom: 0.55rem;
      }

      .ht-date {
        display: flex;
        gap: 0.55rem;
        align-items: center;
      }

      .ht-date-title {
        font-weight: 800;
        font-size: 0.95rem;
        line-height: 1.1;
      }

      .ht-date-sub {
        font-size: 0.75rem;
        color: rgba(0,0,0,0.55);
        margin-top: 0.05rem;
      }

      .ht-streak {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.55rem;
        border-radius: 999px;
        background: rgba(255,75,75,0.12);
        color: rgba(0,0,0,0.78);
        border: 1px solid rgba(255,75,75,0.25);
        font-weight: 800;
        font-size: 0.85rem;
        white-space: nowrap;
      }

      .ht-phone-card {
        background: rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 20px;
        padding: 0.9rem 0.9rem;
        margin-top: 0.65rem;
      }

      .ht-mini-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.6rem;
        align-items: start;
        margin-top: 0.25rem;
      }

      .ht-mini-label {
        font-size: 0.72rem;
        color: rgba(0,0,0,0.55);
        margin-bottom: 0.1rem;
        font-weight: 700;
      }

      .ht-mini-value {
        font-size: 1.25rem;
        font-weight: 900;
        letter-spacing: -0.02em;
      }

      .ht-mini-sub {
        font-size: 0.72rem;
        color: rgba(0,0,0,0.55);
      }

      .ht-macro-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.6rem;
        margin-top: 0.65rem;
      }

      .ht-macro {
        background: rgba(255,255,255,0.65);
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 16px;
        padding: 0.55rem 0.55rem;
      }

      .ht-macro-name {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.78rem;
        font-weight: 800;
        color: rgba(0,0,0,0.70);
        margin-bottom: 0.2rem;
      }

      .ht-bar {
        height: 6px;
        border-radius: 999px;
        background: rgba(0,0,0,0.08);
        overflow: hidden;
      }

      .ht-bar > div {
        height: 100%;
        border-radius: 999px;
        width: 0%;
      }

      .ht-macro-val {
        margin-top: 0.3rem;
        font-size: 0.78rem;
        color: rgba(0,0,0,0.60);
        font-weight: 800;
      }

      .ht-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.6rem;
      }

      .ht-row-title {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-weight: 900;
        color: rgba(0,0,0,0.78);
        font-size: 0.95rem;
      }

      .ht-row-sub {
        color: rgba(0,0,0,0.55);
        font-size: 0.78rem;
        font-weight: 700;
      }

      .ht-water-cups {
        display: flex;
        gap: 0.22rem;
        align-items: flex-end;
      }

      .ht-cup {
        width: 16px;
        height: 22px;
        border-radius: 6px;
        border: 1px solid rgba(0,0,0,0.10);
        background: rgba(56,189,248,0.20);
        position: relative;
        overflow: hidden;
      }

      .ht-cup.fill { background: rgba(56,189,248,0.95); }

      .ht-diary-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.6rem;
        background: rgba(255,255,255,0.65);
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 16px;
        padding: 0.55rem 0.6rem;
        margin-top: 0.55rem;
      }

      .ht-diary-left {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        min-width: 0;
      }

      .ht-diary-img {
        width: 36px;
        height: 36px;
        border-radius: 12px;
        background: rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
      }

      .ht-diary-name {
        font-weight: 900;
        color: rgba(0,0,0,0.80);
        font-size: 0.88rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
      }

      .ht-diary-kcal {
        font-weight: 900;
        color: rgba(255,75,75,0.92);
        font-size: 0.85rem;
      }

      .ht-diary-right {
        color: rgba(0,0,0,0.55);
        font-weight: 800;
        font-size: 0.78rem;
        white-space: nowrap;
      }

      .ht-nav {
        margin-top: 0.65rem;
        background: rgba(255,255,255,0.70);
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 18px;
        padding: 0.55rem 0.55rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.35rem;
        position: relative;
      }

      .ht-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.2rem;
        color: rgba(0,0,0,0.60);
        font-weight: 800;
        font-size: 0.68rem;
        width: 20%;
      }

      .ht-nav-icon {
        width: 34px;
        height: 34px;
        border-radius: 14px;
        background: rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
      }

      .ht-fab {
        width: 54px;
        height: 54px;
        border-radius: 999px;
        background: rgba(255,75,75,0.95);
        color: white;
        font-weight: 900;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 14px 30px rgba(255,75,75,0.35);
        margin-top: -26px;
        border: 1px solid rgba(255,75,75,0.25);
      }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def title(text: str, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="ht-title">{text}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="ht-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def pill(text: str, tone: str = "blue") -> None:
    st.markdown(f'<span class="ht-pill {tone}">{text}</span>', unsafe_allow_html=True)


def section_title(text: str) -> None:
    st.markdown(f'<div class="ht-section-title">{text}</div>', unsafe_allow_html=True)


def card_start(soft: bool = False) -> None:
    cls = "ht-card-soft" if soft else "ht-card"
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)


def card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def kpi_grid(items: list[dict]) -> None:
    html = ['<div class="ht-kpi-grid">']
    for it in items:
        label = it.get("label", "")
        value = it.get("value", "")
        sub = it.get("sub", "")
        html.append('<div class="ht-kpi">')
        html.append(f'<div class="ht-kpi-label">{label}</div>')
        html.append(f'<div class="ht-kpi-value">{value}</div>')
        if sub:
            html.append(f'<div class="ht-kpi-sub">{sub}</div>')
        html.append('</div>')
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def gauge_kcal(remaining: float, goal: float) -> go.Figure:
    goal = max(goal, 1.0)
    remaining = max(min(remaining, goal), 0.0)
    used = max(goal - remaining, 0.0)
    pct = used / goal

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=remaining,
            number={"suffix": " kcal", "font": {"size": 44, "color": "rgba(255,255,255,0.92)"}},
            gauge={
                "axis": {"range": [0, goal], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)"},
                "bar": {"color": "rgba(56,189,248,0.95)"},
                "bgcolor": "rgba(255,255,255,0.06)",
                "borderwidth": 0,
                "steps": [{"range": [0, goal], "color": "rgba(255,255,255,0.06)"}],
                "threshold": {"line": {"color": "rgba(255,75,75,0.9)", "width": 3}, "thickness": 0.75, "value": goal},
            },
            title={"text": "kcal restantes", "font": {"size": 16, "color": "rgba(255,255,255,0.65)"}},
        )
    )
    fig.update_layout(
        height=280,
        margin=dict(l=18, r=18, t=45, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "system-ui, -apple-system, Segoe UI, Roboto, Arial"},
    )
    fig.add_annotation(
        x=0.5,
        y=0.06,
        xref="paper",
        yref="paper",
        text=f"{int(used)} consumidas · {int(pct*100)}%",
        showarrow=False,
        font={"size": 14, "color": "rgba(255,255,255,0.65)"},
    )
    return fig


def phone_shell_start() -> None:
    st.markdown('<div class="ht-phone"><div class="ht-phone-inner">', unsafe_allow_html=True)


def phone_shell_end() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


def phone_top(today_label: str, sublabel: str, streak: int) -> None:
    st.markdown(
        f"""
        <div class="ht-phone-top">
          <div class="ht-date">
            <div class="ht-nav-icon">🗓️</div>
            <div>
              <div class="ht-date-title">{today_label}</div>
              <div class="ht-date-sub">{sublabel}</div>
            </div>
          </div>
          <div class="ht-streak">🔥 {streak}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mini_metrics(left_label: str, left_value: str, right_label: str, right_value: str) -> None:
    st.markdown(
        f"""
        <div class="ht-mini-grid">
          <div>
            <div class="ht-mini-label">{left_label}</div>
            <div class="ht-mini-value">{left_value}</div>
            <div class="ht-mini-sub"></div>
          </div>
          <div style="text-align:right;">
            <div class="ht-mini-label">{right_label}</div>
            <div class="ht-mini-value">{right_value}</div>
            <div class="ht-mini-sub"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def macro_progress(name: str, icon: str, value: float, goal: float, color: str) -> str:
    goal = max(goal, 1.0)
    pct = min(max(value / goal, 0.0), 1.0) * 100
    return (
        '<div class="ht-macro">'
        f'<div class="ht-macro-name">{icon} {name}</div>'
        f'<div class="ht-bar"><div style="width:{pct:.0f}%; background:{color};"></div></div>'
        f'<div class="ht-macro-val">{int(value)}/{int(goal)} g</div>'
        "</div>"
    )


def macros_row(items: list[dict]) -> None:
    html = ['<div class="ht-macro-row">']
    for it in items:
        html.append(
            macro_progress(
                name=it["name"],
                icon=it["icon"],
                value=float(it["value"]),
                goal=float(it["goal"]),
                color=it["color"],
            )
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def water_row(total_ml: int, goal_ml: int, cups: int = 5) -> None:
    goal_ml = max(goal_ml, 1)
    per = goal_ml / cups
    filled = int(min(max(total_ml / per, 0), cups))
    cup_html = []
    for i in range(cups):
        cup_html.append('<div class="ht-cup fill"></div>' if i < filled else '<div class="ht-cup"></div>')
    st.markdown(
        f"""
        <div class="ht-phone-card">
          <div class="ht-row">
            <div>
              <div class="ht-row-title">💧 AGUA</div>
              <div class="ht-row-sub">Objetivo: {goal_ml} ml</div>
            </div>
            <div class="ht-water-cups">{''.join(cup_html)}</div>
          </div>
          <div style="margin-top:0.45rem; font-weight:900; font-size:1.2rem; color: rgba(0,0,0,0.80);">{total_ml} <span style="font-weight:800; font-size:0.85rem; color: rgba(0,0,0,0.55);">ml</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def diary_item(name: str, kcal: int, tag: str) -> None:
    st.markdown(
        f"""
        <div class="ht-diary-item">
          <div class="ht-diary-left">
            <div class="ht-diary-img">🍽️</div>
            <div>
              <div class="ht-diary-name">{name}</div>
              <div class="ht-diary-kcal">🔥 {kcal} calorías</div>
            </div>
          </div>
          <div class="ht-diary-right">{tag}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_bar(active: str = "Nutrición") -> None:
    def item(icon: str, label: str, is_active: bool) -> str:
        c = "rgba(255,75,75,0.95)" if is_active else "rgba(0,0,0,0.60)"
        bg = "rgba(255,75,75,0.10)" if is_active else "rgba(0,0,0,0.04)"
        return (
            '<div class="ht-nav-item">'
            f'<div class="ht-nav-icon" style="color:{c}; background:{bg};">{icon}</div>'
            f"<div style='color:{c};'>{label}</div>"
            "</div>"
        )

    st.markdown(
        f"""
        <div class="ht-nav">
          {item('🍎', 'Nutrición', active=='Nutrición')}
          {item('🏃', 'Fitness', active=='Fitness')}
          <div class="ht-fab">+</div>
          {item('🧠', 'Coach', active=='Coach')}
          {item('📈', 'Progreso', active=='Progreso')}
        </div>
        """,
        unsafe_allow_html=True,
    )
