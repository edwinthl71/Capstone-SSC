"""Late Delivery Risk – Streamlit app for the DataCo supply chain capstone."""
import base64
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from risk_model import BAND_COLOURS, DEFAULTS, DEPTS, MODEL, MODES, PROMISE_DAYS, action, band, predict

HERE = Path(__file__).parent  # files are found next to app.py, wherever the repository puts it
st.set_page_config(page_title="Late Delivery Risk", page_icon=str(HERE / "logo.png"), layout="wide")

NAVY, NAVY2, ORANGE, MUTED, LINE = "#1b3a6b", "#2c4f8a", "#e8792b", "#5b6676", "#e3e8f0"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PAY_NAMES = {1: "Debit", 2: "Transfer", 3: "Cash", 4: "Payment"}  # DataCo payment types (matched via order status)
MODE_NOTE = {"First Class": "promises 1 day", "Second Class": "promises 2 days", "Same Day": "same-day dispatch",
             "Standard Class": "promises 4 days"}
LOGO = base64.b64encode((HERE / "logo.png").read_bytes()).decode()


# ---------------- helpers ----------------
def stretch(fn, *args, **kwargs):
    """Full-width element on any Streamlit version (newer: width='stretch'; older: use_container_width)."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except TypeError:
        return fn(*args, use_container_width=True, **kwargs)


def styled(chart, height=260):
    return (chart.properties(height=height)
            .configure(font="Segoe UI, Inter, system-ui, sans-serif")
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor=MUTED, titleColor=MUTED, gridColor="#edf0f5", domainColor=LINE, tickColor=LINE,
                            labelFontSize=12, titleFontSize=12, titleFontWeight="normal")
            .configure_legend(labelColor=MUTED, titleColor=MUTED, orient="top", labelFontSize=12))


def section(title, sub=""):
    st.markdown(f"<div class='sec'><b>{title}</b>{f'<span>{sub}</span>' if sub else ''}</div>", unsafe_allow_html=True)


def pct(x):
    return f"{x:.0%}"


st.markdown(f"""<style>
#MainMenu, footer, [data-testid="stDecoration"] {{visibility:hidden; height:0}}
[data-testid="stHeader"] {{background:transparent}}
.block-container {{padding-top:1.4rem; padding-bottom:2rem; max-width:1320px}}
.hero {{background:linear-gradient(110deg,{NAVY} 0%,{NAVY2} 70%,#3a64a6 100%); border-radius:18px; padding:22px 28px;
        display:flex; align-items:center; gap:22px; color:#fff; box-shadow:0 10px 30px rgba(27,58,107,.18); margin-bottom:.6rem}}
.hero img {{width:92px; height:auto; background:#fff; border-radius:14px; padding:6px}}
.hero h1 {{color:#fff; font-size:2.05rem; margin:0; padding:0; line-height:1.15}}
.hero p {{margin:.3rem 0 .7rem; color:#d6e1f2; font-size:1rem}}
.chip {{display:inline-block; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25); color:#fff;
        border-radius:999px; padding:3px 12px; font-size:.82rem; margin:0 6px 4px 0}}
.chip.o {{background:{ORANGE}; border-color:{ORANGE}; font-weight:700}}
.sec {{display:flex; align-items:baseline; gap:10px; margin:.2rem 0 .5rem}}
.sec b {{font-size:1.05rem; color:{NAVY}}} .sec span {{color:{MUTED}; font-size:.85rem}}
.lbl {{font-size:.72rem; letter-spacing:.09em; text-transform:uppercase; font-weight:800; color:#8a94a6; margin:.5rem 0 .1rem}}
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {{background:#fff; border:1px solid {LINE} !important;
        border-radius:16px; box-shadow:0 1px 2px rgba(16,24,40,.04),0 6px 18px rgba(16,24,40,.05)}}
[data-testid="stMetric"] {{background:#fff; border:1px solid {LINE}; border-radius:14px; padding:14px 18px;
        box-shadow:0 1px 2px rgba(16,24,40,.04)}}
[data-testid="stMetricLabel"] p {{color:{MUTED}; font-weight:600}}
[data-testid="stMetricValue"] {{color:{NAVY}; font-weight:800}}
.stTabs [data-baseweb="tab-list"] {{gap:6px; border-bottom:1px solid {LINE}}}
.stTabs [data-baseweb="tab"] {{font-weight:700; padding:10px 18px; border-radius:10px 10px 0 0}}
.stTabs [aria-selected="true"] {{color:{NAVY}; background:#fff}}
.res {{display:flex; gap:22px; align-items:center; flex-wrap:wrap}}
.big {{font-size:3.6rem; font-weight:800; line-height:1}}
.pill {{display:inline-block; color:#fff; font-weight:800; letter-spacing:.06em; font-size:.8rem; padding:5px 14px; border-radius:999px}}
.scale {{position:relative; margin:22px 0 6px}}
.scale .bar {{display:flex; height:12px; border-radius:99px; overflow:hidden}}
.scale .bar i {{display:block; height:100%}}
.scale .mk {{position:absolute; top:-9px; width:3px; height:30px; background:#1b2230; border-radius:2px; transform:translateX(-50%)}}
.scale .mk span {{position:absolute; top:-22px; left:50%; transform:translateX(-50%); font-size:.78rem; font-weight:800; white-space:nowrap}}
.scale .ticks {{display:grid; grid-template-columns:repeat(3,1fr); text-align:center; font-size:.75rem; color:{MUTED}; margin-top:6px}}
.act {{border-left:4px solid; border-radius:10px; padding:12px 16px; background:#f7f9fc; margin-top:14px}}
.act b {{display:block; margin-bottom:2px}}
.tip {{background:#fff7ef; border:1px solid #f6d9bd; border-radius:12px; padding:12px 16px; margin-top:12px}}
.empty {{text-align:center; padding:56px 30px; color:{MUTED}}}
.empty h3 {{color:{NAVY}; margin:.4rem 0}}
.steps {{display:flex; gap:12px; justify-content:center; margin-top:18px; flex-wrap:wrap}}
.steps div {{background:#f4f6fa; border-radius:12px; padding:10px 16px; font-size:.9rem}}
.steps b {{color:{ORANGE}; margin-right:6px}}
.cm {{display:grid; grid-template-columns:110px 1fr 1fr; gap:8px; font-size:.85rem; color:{MUTED}}}
.cm .h {{text-align:center; font-weight:700}} .cm .r {{display:flex; align-items:center; font-weight:700}}
.cm .c {{border-radius:12px; text-align:center; padding:16px 6px}} .cm .c b {{display:block; font-size:1.6rem}}
.foot {{color:#8a94a6; font-size:.8rem; text-align:center; margin-top:2rem}}
</style>""", unsafe_allow_html=True)

st.markdown(f"""<div class="hero"><img src="data:image/png;base64,{LOGO}" alt="logo"><div>
<h1>Late Delivery Risk</h1>
<p>Score an order at checkout and see how likely it is to arrive late, using only what is known when it is placed.</p>
<span class="chip o">ROC-AUC 0.77</span><span class="chip">Gradient Boosting</span><span class="chip">65,752 orders · Jan 2015 – Jan 2018</span><span class="chip">DataCo supply chain capstone</span>
</div></div>""", unsafe_allow_html=True)


@st.cache_data
def load_scores() -> pd.DataFrame:
    df = pd.read_csv(HERE / "late_risk_scored_orders.csv", parse_dates=["order_date"])
    df["year"] = df["order_date"].dt.year
    df["payment"] = df["Payment_Type_ID"].map(PAY_NAMES)
    return df


tab_calc, tab_orders, tab_model = st.tabs(["Risk calculator", "Scored orders", "About the model"])

# ---------------- calculator ----------------
with tab_calc:
    left, right = st.columns([5, 7], gap="large")

    with left:
        with st.form("order_form", border=True):
            section("Order at checkout", "fill in, then Predict")
            st.markdown("<div class='lbl'>Shipping</div>", unsafe_allow_html=True)
            mode_name = st.radio("Shipping mode", list(MODES), horizontal=True, key="mode", label_visibility="collapsed")
            st.markdown("<div class='lbl'>When</div>", unsafe_allow_html=True)
            hour = st.slider("Order hour", 0, 23, 14, format="%d:00", key="hour")
            a, b = st.columns(2)
            dow = a.selectbox("Day of week", range(7), index=2, format_func=lambda d: DAYS[d], key="dow")
            month = b.selectbox("Month", range(1, 13), index=5, format_func=lambda m: MONTHS[m - 1], key="month")
            st.markdown("<div class='lbl'>Basket</div>", unsafe_allow_html=True)
            a, b = st.columns(2)
            dept = a.selectbox("Main department", range(len(DEPTS)), index=DEPTS.index("Fitness"), format_func=lambda i: DEPTS[i], key="dept")
            pay_ids = sorted(int(k) for k in MODEL["pay_n"])
            pay = b.selectbox("Payment type", pay_ids, format_func=lambda k: PAY_NAMES.get(k, f"Type {k}"), key="pay")
            n_items = a.number_input("Items in order", 1, 5, int(DEFAULTS["n_items"]), key="items")
            qty = b.number_input("Total quantity", 1, 25, int(DEFAULTS["total_qty"]), key="qty")
            sales = a.number_input("Order value ($)", 5.0, 2500.0, float(round(DEFAULTS["order_sales"])), step=5.0, key="sales")
            disc = b.number_input("Average discount (%)", 0, 25, int(round(DEFAULTS["avg_discount_rate"] * 100)), key="disc")
            submitted = stretch(st.form_submit_button, "Predict late-delivery risk", type="primary")

    if submitted:
        st.session_state["order"] = dict(days_sched=MODES[mode_name], hour=hour, dow=dow, month=month, Payment_Type_ID=pay,
                                         n_items=n_items, total_qty=qty, order_sales=sales, avg_discount_rate=disc / 100, dept_code=dept)
        st.session_state["order_label"] = (f"{mode_name} · {DAYS[dow]} {hour:02d}:00 · {MONTHS[month - 1]} · "
                                           f"{n_items} item(s), ${sales:,.0f} · {DEPTS[dept]} · {PAY_NAMES.get(pay, pay)}")

    with right:
        if "order" not in st.session_state:
            with st.container(border=True):
                st.markdown(f"""<div class="empty"><img src="data:image/png;base64,{LOGO}" width="110" alt="">
<h3>Score an order</h3><div>Enter the order details on the left and click <b>Predict late-delivery risk</b>.</div>
<div class="steps"><div><b>1</b>Choose the shipping mode</div><div><b>2</b>Set time and basket</div><div><b>3</b>Predict and compare</div></div></div>""",
                            unsafe_allow_html=True)
        else:
            order = st.session_state["order"]
            mode, hour_sel = order["days_sched"], order["hour"]
            mode_label = next(n for n, c in MODES.items() if c == mode)
            p = predict(order)
            bnd = band(p)
            col = BAND_COLOURS[bnd]

            with st.container(border=True):
                section("Prediction", st.session_state["order_label"])
                zones = "".join(f"<i style='width:{w}%;background:{c}'></i>" for w, c in
                                [(100 / 3, BAND_COLOURS["Low"]), (100 / 3, BAND_COLOURS["Medium"]), (100 / 3, BAND_COLOURS["High"])])
                st.markdown(f"""<div class="res"><div><div class="big" style="color:{col}">{pct(p)}</div>
<div style="color:{MUTED};font-size:.9rem">chance this order arrives late</div></div>
<div><span class="pill" style="background:{col}">{bnd.upper()} RISK</span>
<div style="color:{MUTED};font-size:.85rem;margin-top:6px">{mode_label} {MODE_NOTE[mode_label]}</div></div></div>
<div class="scale"><div class="bar" style="opacity:.85">{zones}</div><div class="mk" style="left:{min(max(p, .01), .99) * 100:.1f}%"><span>{pct(p)}</span></div>
<div class="ticks"><span>Low · under 33%</span><span>Medium · 33–67%</span><span>High · 67% and above</span></div></div>
<div class="act" style="border-color:{col}"><b>Recommended action</b>{action(bnd)}</div>""", unsafe_allow_html=True)

                alts = {name: predict({**order, "days_sched": code}) for name, code in MODES.items()}
                best_mode = min(alts, key=alts.get)
                hours = {h: predict({**order, "hour": h}) for h in range(24)}
                best_hour = min(hours, key=hours.get)
                tips = []
                if best_mode != mode_label and p - alts[best_mode] >= 0.02:
                    tips.append(f"Switching to <b>{best_mode}</b> lowers the risk to <b>{pct(alts[best_mode])}</b> "
                                f"({(p - alts[best_mode]) * 100:.0f} points lower).")
                if best_hour != hour_sel and p - hours[best_hour] >= 0.02:
                    tips.append(f"Placed at <b>{best_hour:02d}:00</b>, the same order scores <b>{pct(hours[best_hour])}</b>.")
                if not tips:
                    tips.append("This is already close to the lowest risk this order can get by changing mode or order time.")
                st.markdown("<div class='tip'><b>What would lower the risk?</b><br>" + "<br>".join(tips) + "</div>", unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                with st.container(border=True):
                    section("Same order, other modes")
                    dm = pd.DataFrame([{"mode": n, "risk": r, "selected": n == mode_label} for n, r in alts.items()])
                    dm["band"] = dm["risk"].map(band)
                    base = alt.Chart(dm).encode(y=alt.Y("mode:N", sort=list(MODES), title=None, axis=alt.Axis(labelFontWeight="bold")))
                    bars = base.mark_bar(cornerRadiusEnd=5, size=26).encode(
                        x=alt.X("risk:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", title=None, tickCount=5)),
                        color=alt.Color("band:N", scale=alt.Scale(domain=list(BAND_COLOURS), range=list(BAND_COLOURS.values())), legend=None),
                        opacity=alt.condition("datum.selected", alt.value(1), alt.value(0.45)),
                        tooltip=[alt.Tooltip("mode:N", title="Mode"), alt.Tooltip("risk:Q", format=".0%", title="Risk")])
                    text = base.mark_text(align="left", dx=6, fontWeight="bold").encode(
                        x="risk:Q", text=alt.Text("risk:Q", format=".0%"), color=alt.value("#1b2230"))
                    stretch(st.altair_chart, styled(bars + text, 230))
            with g2:
                with st.container(border=True):
                    section("Same order, other times of day")
                    dh = pd.DataFrame([{"hour": h, "risk": r} for h, r in hours.items()])
                    x = alt.X("hour:Q", scale=alt.Scale(domain=[0, 23]), title="Order hour", axis=alt.Axis(tickCount=12))
                    area = alt.Chart(dh).mark_area(line={"color": ORANGE, "strokeWidth": 2.5}, color=ORANGE, opacity=0.12).encode(
                        x=x, y=alt.Y("risk:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", title=None, tickCount=5)),
                        tooltip=[alt.Tooltip("hour:Q", title="Hour"), alt.Tooltip("risk:Q", format=".0%", title="Risk")])
                    rules = alt.Chart(pd.DataFrame({"y": [1 / 3, 2 / 3]})).mark_rule(strokeDash=[4, 4], color="#b8c1d1").encode(y=alt.Y("y:Q", title=None))
                    dot = alt.Chart(dh[dh.hour == hour_sel]).mark_point(filled=True, size=110, color=NAVY, opacity=1).encode(x="hour:Q", y="risk:Q")
                    stretch(st.altair_chart, styled(rules + area + dot, 230))

# ---------------- scored orders ----------------
with tab_orders:
    df = load_scores()
    with st.container(border=True):
        section("Filter the scored orders", "every order scored by the model")
        f1, f2, f3, f4 = st.columns(4)
        years = f1.multiselect("Year", sorted(df.year.unique()), default=sorted(df.year.unique()))
        modes = f2.multiselect("Shipping mode", list(MODES), default=list(MODES))
        bands = f3.multiselect("Risk band", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        depts = f4.multiselect("Department", sorted(df.primary_dept.dropna().unique()), default=[], placeholder="All departments")
    sel = df[df.year.isin(years) & df.ship_mode.isin(modes) & df.risk_band.isin(bands)]
    if depts:
        sel = sel[sel.primary_dept.isin(depts)]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Orders", f"{len(sel):,}")
    k2.metric("Actually late", f"{sel.actual_late.mean():.1%}" if len(sel) else "–")
    k3.metric("Average predicted risk", f"{sel.late_risk.mean():.1%}" if len(sel) else "–")
    k4.metric("High-risk orders", f"{(sel.risk_band == 'High').sum():,}")

    if len(sel):
        s1, s2 = st.columns(2)
        with s1:
            with st.container(border=True):
                section("Orders by risk band", "label = share actually late")
                bc = (sel.groupby("risk_band").agg(orders=("Order Id", "size"), late=("actual_late", "mean"))
                      .reindex(["High", "Medium", "Low"]).dropna().reset_index())
                base = alt.Chart(bc).encode(y=alt.Y("risk_band:N", sort=["High", "Medium", "Low"], title=None, axis=alt.Axis(labelFontWeight="bold")))
                bars = base.mark_bar(cornerRadiusEnd=5, size=30).encode(
                    x=alt.X("orders:Q", title="Orders"),
                    color=alt.Color("risk_band:N", scale=alt.Scale(domain=list(BAND_COLOURS), range=list(BAND_COLOURS.values())), legend=None),
                    tooltip=[alt.Tooltip("risk_band:N", title="Band"), alt.Tooltip("orders:Q", format=",", title="Orders"),
                             alt.Tooltip("late:Q", format=".1%", title="Actually late")])
                text = base.mark_text(align="left", dx=6, color="#1b2230").encode(
                    x="orders:Q", text=alt.Text("late:Q", format=".0%"))
                stretch(st.altair_chart, styled(bars + text, 230))
        with s2:
            with st.container(border=True):
                section("Predicted vs actual late rate", "by shipping mode")
                mm = (sel.groupby("ship_mode").agg(Predicted=("late_risk", "mean"), Actual=("actual_late", "mean"))
                      .reindex([m for m in MODES if m in set(sel.ship_mode)]).reset_index().melt("ship_mode"))
                ch = alt.Chart(mm).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X("ship_mode:N", sort=list(MODES), title=None, axis=alt.Axis(labelAngle=0)), xOffset="variable:N",
                    y=alt.Y("value:Q", axis=alt.Axis(format="%", title=None, tickCount=5), scale=alt.Scale(domain=[0, 1])),
                    color=alt.Color("variable:N", scale=alt.Scale(domain=["Predicted", "Actual"], range=[NAVY2, ORANGE]), title=None),
                    tooltip=[alt.Tooltip("ship_mode:N", title="Mode"), alt.Tooltip("variable:N", title=" "), alt.Tooltip("value:Q", format=".1%", title="Rate")])
                stretch(st.altair_chart, styled(ch, 230))

        with st.container(border=True):
            section("Highest-risk orders in this selection", "top 500")
            top = (sel.sort_values("late_risk", ascending=False).head(500)
                   [["Order Id", "order_date", "ship_mode", "primary_dept", "payment", "hour", "n_items", "order_sales", "late_risk", "risk_band", "actual_late"]])
            top["actual_late"] = top["actual_late"].map({1: "Late", 0: "On time"})
            cfg = {"Order Id": st.column_config.NumberColumn("Order", format="%d"),
                   "order_date": st.column_config.DatetimeColumn("Order date", format="D MMM YYYY, HH:mm"),
                   "ship_mode": "Shipping mode", "primary_dept": "Department", "payment": "Payment",
                   "hour": st.column_config.NumberColumn("Hour", format="%d:00"),
                   "n_items": "Items", "order_sales": st.column_config.NumberColumn("Value", format="$%.0f"),
                   "late_risk": st.column_config.ProgressColumn("Late risk", format="%.0f%%", min_value=0, max_value=100),
                   "risk_band": "Band", "actual_late": "Actual"}
            top["late_risk"] = (top["late_risk"] * 100).round(1)
            stretch(st.dataframe, top, hide_index=True, column_config=cfg, height=380)
            st.download_button("Download this selection (CSV)", sel.drop(columns=["year", "payment"]).to_csv(index=False).encode(),
                               "late_risk_selection.csv", "text/csv")
    else:
        st.info("No orders match these filters.")

# ---------------- model ----------------
with tab_model:
    a, b, c, d = st.columns(4)
    a.metric("ROC-AUC (hold-out)", "0.770")
    b.metric("Precision", "86%", help="Of the orders flagged late, the share that really were late.")
    c.metric("Recall", "58%", help="Of the orders that were late, the share the model flagged.")
    d.metric("Accuracy", "72%")
    m1, m2 = st.columns([6, 5], gap="large")
    with m1:
        with st.container(border=True):
            section("How the model works")
            st.markdown("""
- **Model:** Gradient Boosting (100 trees, depth 3), 80/20 stratified split, trained on `fact_orders`.
- **Inputs, all known at checkout:** shipping mode, order hour, day of week, month, payment type, items, quantity, order value, discount and department.
- **No leakage:** actual shipping days and delivery status are left out because they are only known after delivery.
- **Biggest driver:** shipping mode. Order hour comes second, consistent with a dispatch cut-off.
- **Risk bands** (same as the notebook): Low below 33%, Medium 33–67%, High 67% and above.
""")
            cal = pd.DataFrame({"band": ["Low", "Medium", "High"], "late": [0.22, 0.39, 0.86]})
            base = alt.Chart(cal).encode(x=alt.X("band:N", sort=["Low", "Medium", "High"], title=None, axis=alt.Axis(labelAngle=0, labelFontWeight="bold")))
            bars = base.mark_bar(cornerRadiusEnd=5, size=56).encode(
                y=alt.Y("late:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", title="Actually late", tickCount=5)),
                color=alt.Color("band:N", scale=alt.Scale(domain=list(BAND_COLOURS), range=list(BAND_COLOURS.values())), legend=None))
            text = base.mark_text(dy=-10, fontWeight="bold", color="#1b2230").encode(y="late:Q", text=alt.Text("late:Q", format=".0%"))
            st.markdown("<div class='lbl'>Bands are well separated: share of orders actually late, out-of-fold</div>", unsafe_allow_html=True)
            stretch(st.altair_chart, styled(bars + text, 210))
    with m2:
        with st.container(border=True):
            section("Confusion matrix", "13,151 test orders · 50% cut-off")
            st.markdown("""<div class="cm"><div></div><div class="h">Predicted late</div><div class="h">Predicted on time</div>
<div class="r">Actually late</div><div class="c" style="background:#e3f2ea"><b style="color:#2f8a5f">4,157</b>caught</div>
<div class="c" style="background:#fbe6e9"><b style="color:#c93f52">3,053</b>missed</div>
<div class="r">Actually on time</div><div class="c" style="background:#fdeedd"><b style="color:#c9700b">678</b>false alarms</div>
<div class="c" style="background:#eef1f6"><b style="color:#1b3a6b">5,263</b>correct on time</div></div>""", unsafe_allow_html=True)
            st.caption("When the model flags an order it is right 86% of the time, and it catches 58% of late orders. "
                       "Lowering the cut-off catches more late orders at the cost of more false alarms.")

st.markdown("<div class='foot'>DataCo supply chain capstone · Late Delivery Risk Prediction · Predictions are estimates for decision support.</div>",
            unsafe_allow_html=True)
