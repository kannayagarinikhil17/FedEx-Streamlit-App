import streamlit as st
import pandas as pd
import plotly.express as px

# ──────────────────────────────────────────────────────────────
# 🔧 Page Config & Sidebar
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Supply Chain Delay Analysis", layout="wide")

st.sidebar.title("Navigation")
PAGES = [
    "Welcome",
    "Delay & Pricing Patterns",
    "Top Contributors",
    "Conclusion & Insights",
]
page = st.sidebar.radio("Select Page:", PAGES)

st.sidebar.title("Upload Dataset")
file = st.sidebar.file_uploader("Upload your CSV", type=["csv"], key="uploader")

# ──────────────────────────────────────────────────────────────
# 📦 Read & Feature‑Engineer
# ──────────────────────────────────────────────────────────────
if file:
    df = pd.read_csv(file)

    # Ensure date columns are parsed correctly
    for col in ["Delivered to Client Date", "Scheduled Delivery Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
        else:
            st.error(f"❌ Missing column: {col}")
            st.stop()

    # Create delay and label columns
    df["delivery_delay"] = (df["Delivered to Client Date"] - df["Scheduled Delivery Date"]).dt.days
    df["Delay Label"] = df["delivery_delay"].apply(lambda d: "Early/On-Time" if d <= 0 else "Delayed")
else:
    df = None

# ──────────────────────────────────────────────────────────────
# 1️⃣ Welcome
# ──────────────────────────────────────────────────────────────
if page == "Welcome":
    st.title("🚚 Supply Chain Delay & Pricing Analysis")
    st.markdown(
        """
### Why this app?
Explore how delivery delays and pricing factors impact performance across vendors, managers, and shipment modes.

— **Sections** —  
*Delay & Pricing Patterns* → KPI vs delay deep-dives.  
*Top Contributors*         → Worst performers by delay and cost.  
*Conclusion & Insights*    → Key takeaways and next steps.

- Sample Dataset → [link](https://drive.google.com/file/d/1h02g6ObGWiTID990u2pWTw5o3aNEYzSb/view?usp=sharing)
        """
    )

# ──────────────────────────────────────────────────────────────
# 2️⃣ Delay & Pricing Patterns
# ──────────────────────────────────────────────────────────────
if page == "Delay & Pricing Patterns":
    st.title("Delay & Pricing Patterns")

    if df is None:
        st.warning("➡️ Please upload a dataset to view this analysis.")
        st.stop()

    st.markdown("Focus KPIs: **Delivery Delay**, **Pack Price**, **Line Item Value** vs Delay Status.")

    fig_delay = px.box(df, x="Delay Label", y="delivery_delay", template="plotly_white")
    fig_delay.update_traces(marker_color="#1f77b4")
    fig_delay.update_layout(title="Delivery Delay Distribution", xaxis_title="Delay Status", yaxis_title="Delay (days)")
    st.plotly_chart(fig_delay, use_container_width=True)

    if "Shipment Mode" in df.columns:
        fig_pack = px.box(df, x="Shipment Mode", y="Pack Price", template="plotly_white", color="Delay Label")
        fig_pack.update_layout(title="Pack Price by Shipment Mode", xaxis_title="Shipment Mode", yaxis_title="Pack Price")
        st.plotly_chart(fig_pack, use_container_width=True)

    fig_value = px.box(df, x="Delay Label", y="Line Item Value", template="plotly_white", color="Delay Label")
    fig_value.update_layout(title="Line Item Value by Delay Status", xaxis_title="Delay Status", yaxis_title="Line Item Value")
    st.plotly_chart(fig_value, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# 3️⃣ Top Contributors
# ──────────────────────────────────────────────────────────────
if page == "Top Contributors":
    st.title("Top Contributors to Delay & Cost")

    if df is None:
        st.warning("➡️ Please upload a dataset to view this analysis.")
        st.stop()

    st.markdown("Which vendors, managers, and shipment modes contribute most to delays and pricing issues?")

    if "Vendor" in df.columns:
        vendors = (
            df.groupby("Vendor")[["delivery_delay", "Pack Price", "Line Item Value"]]
            .mean()
            .sort_values("delivery_delay", ascending=False)
            .head(10)
            .reset_index()
        )
        fig_vendors = px.bar(
            vendors,
            x="Vendor",
            y=["delivery_delay", "Pack Price", "Line Item Value"],
            barmode="group",
            template="plotly_white",
            labels={"value": "Avg Value", "variable": "Metric"},
        )
        fig_vendors.update_layout(title="Top Vendors by Delay / Pack Price / Value", xaxis_title="Vendor", yaxis_title="Avg Value")
        st.plotly_chart(fig_vendors, use_container_width=True)

    if "Managed By" in df.columns:
        managers = (
            df.groupby("Managed By")[["delivery_delay", "Pack Price", "Line Item Value"]]
            .mean()
            .sort_values("delivery_delay", ascending=False)
            .head(10)
            .reset_index()
        )
        fig_managers = px.bar(
            managers,
            x="Managed By",
            y=["delivery_delay", "Pack Price", "Line Item Value"],
            barmode="group",
            template="plotly_white",
            labels={"value": "Avg Value", "variable": "Metric"},
        )
        fig_managers.update_layout(title="Top Managers by Delay / Pack Price / Value", xaxis_title="Manager", yaxis_title="Avg Value")
        st.plotly_chart(fig_managers, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# 4️⃣ Conclusion & Insights
# ──────────────────────────────────────────────────────────────
if page == "Conclusion & Insights":
    st.title("Conclusion & Insights")
    st.markdown(
        """
### Key Findings
* **Delivery delays** are concentrated among specific vendors and shipment modes.  
* **High pack prices** often correlate with air shipments and delay risk.  
* **Line item value** does not consistently predict delay, but extreme values appear in both categories.

### Strategic Actions
1. Prioritize delay-prone vendors and shipment modes for intervention.  
2. Use predictive analytics to flag high-risk deliveries.  
3. Optimize freight planning for high-value items.

### Future Exploration
- Can premium shipping reduce delay rates for critical items?  
- Which manager-vendor pairs consistently outperform others?  
- How do seasonal trends affect delay and pricing?
        """
    )
