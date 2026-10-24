import altair as alt
import pandas as pd
import streamlit as st

from risk_model import BAND_COLOURS, DEFAULTS, DEPTS, MODEL, MODES, PROMISE_DAYS, action, band, predict

st.set_page_config(page_title="Late Delivery Risk", page_icon="logo.png", layout="wide")

c1, c2 = st.columns([5, 1])
with c1:
    st.title("Late Delivery Risk")
    st.caption("DataCo supply chain capstone · Gradient Boosting on order-time fields · 65,752 orders, Jan 2015 – Jan 2018")
with c2:
    st.image("logo.png", width=120)


@st.cache_data
def load_scores() -> pd.DataFrame:
    df = pd.read_csv("late_risk_scored_orders.csv", parse_dates=["order_date"])
    df["year"] = df["order_date"].dt.year
    return df


tab_calc, tab_orders, tab_model = st.tabs(["Risk calculator", "Scored orders", "Model"])

# ---------------- calculator ----------------
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

with tab_calc:
    left, right = st.columns([5, 7], gap="large")

    with left:
        with st.form("order_form", border=True):
            st.subheader("Order at checkout")
            st.caption("Fill in the order details, then click **Predict**.")
            mode_name = st.radio("Shipping mode", list(MODES), horizontal=True, key="mode",
                                 help="First Class promises 1 day, Second Class 2 days, Same Day same-day dispatch, Standard 4 days.")
            hour = st.slider("Order hour", 0, 23, 14, format="%d:00", key="hour")
            a, b = st.columns(2)
            dow = a.selectbox("Day of week", range(7), index=2, format_func=lambda d: DAYS[d], key="dow")
            month = b.selectbox("Month", range(1, 13), index=5, format_func=lambda m: MONTHS[m - 1], key="month")
            pay_ids = sorted(int(k) for k in MODEL["pay_n"])
            pay = a.selectbox("Payment type", pay_ids, format_func=lambda k: f"Type {k} ({MODEL['pay_n'][str(k)]:,} orders)", key="pay")
            dept = b.selectbox("Main department", range(len(DEPTS)), index=DEPTS.index("Fitness"), format_func=lambda i: DEPTS[i], key="dept")
            n_items = a.number_input("Items in order", 1, 5, int(DEFAULTS["n_items"]), key="items")
            qty = b.number_input("Total quantity", 1, 25, int(DEFAULTS["total_qty"]), key="qty")
            sales = a.number_input("Order value ($)", 5.0, 2500.0, float(round(DEFAULTS["order_sales"])), step=5.0, key="sales")
            disc = b.number_input("Average discount (%)", 0, 25, int(round(DEFAULTS["avg_discount_rate"] * 100)), key="disc")
            submitted = st.form_submit_button("Predict", type="primary", use_container_width=True)

    if submitted:
        st.session_state["order"] = dict(days_sched=MODES[mode_name], hour=hour, dow=dow, month=month, Payment_Type_ID=pay,
                                         n_items=n_items, total_qty=qty, order_sales=sales, avg_discount_rate=disc / 100, dept_code=dept)
        st.session_state["order_label"] = (f"{mode_name} · {DAYS[dow]} {hour:02d}:00 · {MONTHS[month - 1]} · "
                                           f"{n_items} item(s), ${sales:,.0f} · {DEPTS[dept]}")

    with right:
        if "order" not in st.session_state:
            st.info("Enter the order details on the left and click **Predict** to see the late-delivery risk, "
                    "how it compares across shipping modes, and how it changes with order time.")
        else:
            order = st.session_state["order"]
            mode, hour_sel = order["days_sched"], order["hour"]
            p = predict(order)
            bnd = band(p)
            st.caption(f"Prediction for: {st.session_state['order_label']}")
            m1, m2 = st.columns([1, 2])
            m1.metric("Predicted late risk", f"{p:.0%}")
            m2.markdown(f"<span style='background:{BAND_COLOURS[bnd]};color:white;padding:4px 12px;border-radius:999px;font-weight:700'>"
                        f"{bnd.upper()} RISK</span><br><br>{action(bnd)}", unsafe_allow_html=True)
            st.progress(min(max(p, 0.0), 1.0), text="Low < 45% · Medium 45–70% · High ≥ 70%")

            g1, g2 = st.columns(2)
            with g1:
                st.markdown("**Same order, other modes**")
                dm = pd.DataFrame([{"mode": name, "risk": predict({**order, "days_sched": code}), "selected": code == mode}
                                   for name, code in MODES.items()])
                dm["band"] = dm["risk"].map(band)
                ch = alt.Chart(dm).mark_bar(cornerRadius=3).encode(
                    x=alt.X("risk:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", title=None)),
                    y=alt.Y("mode:N", sort=list(MODES), title=None),
                    color=alt.Color("band:N", scale=alt.Scale(domain=list(BAND_COLOURS), range=list(BAND_COLOURS.values())), legend=None),
                    opacity=alt.condition("datum.selected", alt.value(1), alt.value(0.55)),
                    tooltip=["mode", alt.Tooltip("risk:Q", format=".0%")])
                labels = ch.mark_text(align="left", dx=4).encode(text=alt.Text("risk:Q", format=".0%"), color=alt.value("#5d6a80"))
                st.altair_chart(ch + labels, use_container_width=True)
            with g2:
                st.markdown("**Same order, other times of day**")
                dh = pd.DataFrame([{"hour": h, "risk": predict({**order, "hour": h})} for h in range(24)])
                area = alt.Chart(dh).mark_area(line={"color": "#ea7a1e"}, color="#ea7a1e", opacity=0.15).encode(
                    x=alt.X("hour:Q", scale=alt.Scale(domain=[0, 23]), title="Order hour"),
                    y=alt.Y("risk:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", title=None)),
                    tooltip=["hour", alt.Tooltip("risk:Q", format=".0%")])
                dot = alt.Chart(dh[dh.hour == hour_sel]).mark_point(filled=True, size=80, color="#17223a").encode(x="hour:Q", y="risk:Q")
                st.altair_chart(area + dot, use_container_width=True)

# ---------------- scored orders ----------------
with tab_orders:
    df = load_scores()
    f1, f2, f3, f4 = st.columns(4)
    years = f1.multiselect("Year", sorted(df.year.unique()), default=sorted(df.year.unique()))
    modes = f2.multiselect("Shipping mode", sorted(df.ship_mode.unique()), default=sorted(df.ship_mode.unique()))
    bands = f3.multiselect("Risk band", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    depts = f4.multiselect("Department", sorted(df.primary_dept.dropna().unique()), default=[])
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
            st.markdown("**Orders by risk band**")
            bc = sel.groupby("risk_band").agg(orders=("Order Id", "size"), late=("actual_late", "mean")).reindex(["High", "Medium", "Low"]).dropna().reset_index()
            st.altair_chart(alt.Chart(bc).mark_bar(cornerRadius=3).encode(
                x=alt.X("orders:Q", title="Orders"), y=alt.Y("risk_band:N", sort=["High", "Medium", "Low"], title=None),
                color=alt.Color("risk_band:N", scale=alt.Scale(domain=list(BAND_COLOURS), range=list(BAND_COLOURS.values())), legend=None),
                tooltip=["risk_band", "orders", alt.Tooltip("late:Q", format=".1%", title="actually late")]), use_container_width=True)
        with s2:
            st.markdown("**Predicted risk vs actual late rate, by shipping mode**")
            mm = sel.groupby("ship_mode").agg(predicted=("late_risk", "mean"), actual=("actual_late", "mean")).reset_index().melt("ship_mode")
            st.altair_chart(alt.Chart(mm).mark_bar().encode(
                x=alt.X("ship_mode:N", title=None), xOffset="variable:N",
                y=alt.Y("value:Q", axis=alt.Axis(format="%", title=None), scale=alt.Scale(domain=[0, 1])),
                color=alt.Color("variable:N", scale=alt.Scale(range=["#2c4f8a", "#ea7a1e"]), title=None),
                tooltip=["ship_mode", "variable", alt.Tooltip("value:Q", format=".1%")]), use_container_width=True)
        st.markdown("**Highest-risk orders in this selection**")
        st.dataframe(sel.sort_values("late_risk", ascending=False).head(500), use_container_width=True, hide_index=True)
        st.download_button("Download this selection (CSV)", sel.to_csv(index=False).encode(), "late_risk_selection.csv", "text/csv")

# ---------------- model ----------------
with tab_model:
    a, b, c, d = st.columns(4)
    a.metric("ROC-AUC (hold-out)", "0.770")
    b.metric("Precision", "86%")
    c.metric("Recall", "58%")
    d.metric("Accuracy", "72%")
    st.markdown("""
- **Model:** Gradient Boosting (100 trees, depth 3), 80/20 stratified split, retrained on `fact_orders`.
- **Features (known at order time):** shipping mode, order hour, day of week, month, payment type, items, quantity, order value, discount, department.
- **Bands:** Low < 45% · Medium 45–70% · High ≥ 70%. In out-of-fold scoring, 36% / 65% / 89% of orders in each band were actually late.
- **Biggest driver:** shipping mode; order hour is second, consistent with a dispatch cut-off effect.
""")
    cm = pd.DataFrame({"Predicted on time": [5263, 3053], "Predicted late": [678, 4157]}, index=["Actually on time", "Actually late"])
    st.markdown("**Confusion matrix (13,151 test orders, 50% cut-off)**")
    st.dataframe(cm, use_container_width=False)
