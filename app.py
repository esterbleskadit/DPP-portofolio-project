import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

# 1. Page Configuration
st.set_page_config(
    page_title="E-Commerce Churn & Sustainability Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Header & Overview
st.title("E-Commerce Churn & Sustainability Analytics")
st.caption(
    "Analysing Customer Retention, Logistics Distance, and CO2 Emissions"
)


# 3. Data Loading with Caching
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/clean_data.csv")


try:
    df_raw = load_data()
    df = df_raw.copy()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")

    # Preferred Category Filter
    if "PreferedOrderCat" in df.columns:
        cat_opts = df["PreferedOrderCat"].dropna().unique().tolist()
        cat_filter = st.sidebar.multiselect(
            "Product Category:", options=cat_opts, default=cat_opts
        )
        df = df[df["PreferedOrderCat"].isin(cat_filter)]

    # Tenure Filter
    if "TenureBucket" in df.columns:
        tenure_opts = df["TenureBucket"].dropna().unique().tolist()
        tenure_filter = st.sidebar.multiselect(
            "Tenure:", options=tenure_opts, default=tenure_opts
        )
        df = df[df["TenureBucket"].isin(tenure_filter)]

    # City Tier Filter
    if "CityTier" in df.columns:
        city_opts = sorted(df["CityTier"].dropna().unique().tolist())
        city_filter = st.sidebar.multiselect(
            "City Tier:", options=city_opts, default=city_opts
        )
        df = df[df["CityTier"].isin(city_filter)]

    # Warehouse Distance Slider
    if "WarehouseToHome" in df.columns:
        min_d, max_d = int(df["WarehouseToHome"].min()), int(
            df["WarehouseToHome"].max()
        )
        max_dist = st.sidebar.slider(
            "Warehouse Distance (km):",
            min_value=min_d,
            max_value=max_d,
            value=max_d,
        )
        df = df[df["WarehouseToHome"] <= max_dist]

    st.sidebar.divider()

    # --- TOP KPI METRICS ---
    st.markdown("### Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_customers = len(df)
    churn_rate = (df["Churn"].mean() * 100) if "Churn" in df.columns else 0
    total_returns = (
        df["Estimated_Returns"].sum() if "Estimated_Returns" in df.columns else 0
    )
    total_co2 = (
        df["Estimated_CO2_kg"].sum() if "Estimated_CO2_kg" in df.columns else 0
    )

    kpi1.metric("Total Customers", f"{total_customers:,}")
    kpi2.metric("Churn Rate", f"{churn_rate:.1f}%", delta="-1.2% YoY", delta_color="inverse")
    kpi3.metric("Estimated Returns", f"{int(total_returns):,}")
    kpi4.metric("Carbon Footprint", f"{total_co2 / 1000:,.2f} Tons CO2")

    st.divider()

    # --- NAVIGATION TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Sustainability & Logistics",
        "Risk Simulator",
        "Raw Data",
    ])

    # ==========================================
    # TAB 1: OVERVIEW
    # ==========================================
    with tab1:
        # TOP ROW: 2 CHARTS
        row1_col1, row1_col2 = st.columns(2)

        # 1. Customer Retention Ratio
        with row1_col1:
            st.subheader("Overall Customer Retention")
            churn_counts = df["Churn"].value_counts().to_dict()
            opt_donut = {
                "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
                "legend": {"top": "bottom"},
                "series": [{
                    "name": "Churn Status",
                    "type": "pie",
                    "radius": ["45%", "75%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
                    "label": {"show": False, "position": "center"},
                    "emphasis": {
                        "label": {"show": True, "fontSize": "18", "fontWeight": "bold"}
                    },
                    "data": [
                        {"value": churn_counts.get(0, 0), "name": "Retained", "itemStyle": {"color": "#5470C6"}},
                        {"value": churn_counts.get(1, 0), "name": "Churned", "itemStyle": {"color": "#EE6666"}},
                    ],
                }],
            }
            st_echarts(options=opt_donut, height="320px")

        # 2. Cohort Behavioral Profile (Retained vs Churned)
        with row1_col2:
            st.subheader("Customer Behavior Patterns")
            radar_cols = [
                "HourSpendOnApp",
                "NumberOfDeviceRegistered",
                "CouponUsed",
                "SatisfactionScore",
                "OrderAmountHikeFromlastYear",
            ]
            df_norm = df[radar_cols].copy()
            for col in radar_cols:
                min_v, max_v = df_norm[col].min(), df_norm[col].max()
                df_norm[col] = (
                    (df_norm[col] - min_v) / (max_v - min_v) * 100
                    if max_v > min_v
                    else 0
                )
            df_norm["Churn"] = df["Churn"]
            radar_avg = df_norm.groupby("Churn")[radar_cols].mean().round(1)

            opt_radar = {
                "tooltip": {},
                "legend": {"data": ["Retained", "Churned"], "top": "bottom"},
                "radar": {"indicator": [{"name": col, "max": 100} for col in radar_cols]},
                "series": [{
                    "type": "radar",
                    "data": [
                        {
                            "value": radar_avg.loc[0].tolist() if 0 in radar_avg.index else [0] * 5,
                            "name": "Retained",
                            "itemStyle": {"color": "#5470C6"},
                            "areaStyle": {"opacity": 0.2},
                        },
                        {
                            "value": radar_avg.loc[1].tolist() if 1 in radar_avg.index else [0] * 5,
                            "name": "Churned",
                            "itemStyle": {"color": "#EE6666"},
                            "areaStyle": {"opacity": 0.2},
                        },
                    ],
                }],
            }
            st_echarts(options=opt_radar, height="320px")

        st.divider()

        # BOTTOM ROW: 3 CHARTS
        row2_col1, row2_col2, row2_col3 = st.columns(3)

        # 1. Churn Rate by Product Category
        with row2_col1:
            if "PreferedOrderCat" in df.columns:
                st.subheader("Churn Rate by Product Category")
                cat_churn = (
                    df.groupby("PreferedOrderCat")["Churn"].mean() * 100
                ).round(1).sort_values(ascending=True)

                opt_cat = {
                    "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"},
                    "xAxis": {"type": "value", "name": "Churn Rate (%)"},
                    "yAxis": {"type": "category", "data": cat_churn.index.tolist()},
                    "series": [{
                        "data": cat_churn.values.tolist(),
                        "type": "bar",
                        "itemStyle": {"color": "#91CC75", "borderRadius": [0, 4, 4, 0]},
                    }],
                }
                st_echarts(options=opt_cat, height="300px")

        # 2. Churn Risk by Payment Method
        with row2_col2:
            st.subheader("Churn Risk by Payment Method")
            pay_churn = (
                (df.groupby("PreferredPaymentMode")["Churn"].mean() * 100)
                .round(1)
                .sort_values()
            )
            opt_pay = {
                "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"},
                "xAxis": {"type": "value", "name": "Churn (%)"},
                "yAxis": {"type": "category", "data": pay_churn.index.tolist()},
                "series": [{
                    "data": pay_churn.values.tolist(),
                    "type": "bar",
                    "itemStyle": {"color": "#73C0DE", "borderRadius": [0, 4, 4, 0]},
                }],
            }
            st_echarts(options=opt_pay, height="300px")

        # 3. Churn Rate by Onboarding Phase
        with row2_col3:
            st.subheader("Churn Rate by Onboarding Phase")
            tenure_churn = (
                df.groupby("TenureBucket")["Churn"].mean() * 100
            ).round(1)
            opt_tenure = {
                "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"},
                "xAxis": {"type": "category", "data": tenure_churn.index.tolist()},
                "yAxis": {"type": "value", "name": "Churn Rate (%)", "max": 100},
                "series": [{
                    "data": tenure_churn.values.tolist(),
                    "type": "bar",
                    "showBackground": True,
                    "backgroundStyle": {"color": "rgba(180, 180, 180, 0.1)"},
                    "itemStyle": {
                        "color": {
                            "type": "linear",
                            "x": 0, "y": 0, "x2": 0, "y2": 1,
                            "colorStops": [
                                {"offset": 0, "color": "#EE6666"},
                                {"offset": 1, "color": "#FAC858"},
                            ],
                        }
                    },
                }],
            }
            st_echarts(options=opt_tenure, height="300px")

    # ==========================================
    # TAB 2: SUSTAINABILITY & LOGISTICS
    # ==========================================
    with tab2:
        st.info(
            "**What is ESG in this context?**\n\n"
            "**ESG** stands for **Environmental, Social, and Governance**. In e-commerce operations, "
            "we focus on the **Environmental** pillar: quantifying how customer dissatisfaction, delivery distances, "
            "and product returns create unnecessary transportation mileage and drive up carbon (CO2) emissions."
        )

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("CO2 Emissions & Returns by Complaint")
            esg_grp = df.groupby("Complain")[["Estimated_Returns", "Estimated_CO2_kg"]].sum()
            opt_esg = {
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Estimated Returns", "CO2 Emission (kg)"]},
                "xAxis": {"type": "category", "data": ["No Complaint", "Complaint Registered"]},
                "yAxis": [
                    {"type": "value", "name": "Returns"},
                    {"type": "value", "name": "CO2 (kg)"},
                ],
                "series": [
                    {
                        "name": "Estimated Returns",
                        "type": "bar",
                        "data": esg_grp["Estimated_Returns"].tolist(),
                        "itemStyle": {"color": "#3BA272"},
                    },
                    {
                        "name": "CO2 Emission (kg)",
                        "type": "bar",
                        "yAxisIndex": 1,
                        "data": esg_grp["Estimated_CO2_kg"].tolist(),
                        "itemStyle": {"color": "#FC8452"},
                    },
                ],
            }
            st_echarts(options=opt_esg, height="360px")

        with col_chart2:
            st.subheader("Complaints vs Warehouse Distance")
            dist_comp = df.groupby(["DistanceCategory", "Complain"]).size().unstack(fill_value=0)
            opt_dist = {
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["No Complaint", "Complaint"]},
                "xAxis": {"type": "category", "data": dist_comp.index.tolist()},
                "yAxis": {"type": "value", "name": "Customer Count"},
                "series": [
                    {"name": "No Complaint", "type": "bar", "stack": "total", "data": dist_comp[0].tolist(), "itemStyle": {"color": "#91CC75"}},
                    {"name": "Complaint", "type": "bar", "stack": "total", "data": dist_comp[1].tolist(), "itemStyle": {"color": "#EE6666"}},
                ],
            }
            st_echarts(options=opt_dist, height="360px")

        st.divider()

        st.subheader("CO2 Reduction Simulator")
        st.markdown("Estimate potential carbon and cost reductions by resolving customer complaints.")

        sim_col1, sim_col2 = st.columns([1, 2])
        with sim_col1:
            complaint_reduction = st.slider(
                "Target Complaint Reduction (%):",
                min_value=5, max_value=50, value=20, step=5
            )
            cost_per_return = st.number_input("Avg Logistics Cost per Return (€):", value=12.50)

        with sim_col2:
            complaint_co2 = df[df["Complain"] == 1]["Estimated_CO2_kg"].sum()
            complaint_returns = df[df["Complain"] == 1]["Estimated_Returns"].sum()

            saved_co2 = (complaint_co2 * (complaint_reduction / 100)) / 1000  # tons
            saved_cost = complaint_returns * (complaint_reduction / 100) * cost_per_return

            sc1, sc2 = st.columns(2)
            sc1.metric("Projected CO2 Saved", f"{saved_co2:.2f} Tons", delta=f"-{complaint_reduction}% Emissions")
            sc2.metric("Projected Cost Savings", f"€{saved_cost:,.2f}", delta=f"-{complaint_reduction}% Expenses")
            st.success(f"Achieving a {complaint_reduction}% reduction in complaints eliminates {saved_co2:.1f} tons of carbon emissions from reverse logistics.")

    # ==========================================
    # TAB 3: RISK SIMULATOR
    # ==========================================
    with tab3:
        st.subheader("Customer Churn Risk Calculator")
        st.markdown("Simulate individual customer parameters to inspect churn probability.")

        sim_left, sim_right = st.columns([1, 1])

        with sim_left:
            tenure_val = st.slider("Tenure (Months):", 0, 36, 2)
            recency_val = st.slider("Days Since Last Order:", 0, 30, 10)

            satisfaction_val = st.slider("Satisfaction Score (1-5):", 1, 5, 2)
            complain_val = st.radio("Complaint?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

            distance_val = st.slider("Warehouse Distance (km):", 5, 100, 35)

            # Risk Score Calculation Logic
            base_risk = 40
            if tenure_val < 3: base_risk += 20
            if recency_val > 15: base_risk += 15
            if satisfaction_val <= 2: base_risk += 15
            if complain_val == 1: base_risk += 15
            if distance_val > 30: base_risk += 10
            risk_score = min(max(base_risk, 5), 98)

        with sim_right:
            gauge_color = "#91CC75" if risk_score < 40 else "#FAC858" if risk_score < 70 else "#EE6666"

            opt_gauge = {
                "series": [{
                    "type": "gauge",
                    "startAngle": 180,
                    "endAngle": 0,
                    "min": 0,
                    "max": 100,
                    "pointer": {"show": True},
                    "progress": {"show": True, "width": 18},
                    "axisLine": {"lineStyle": {"width": 18}},
                    "axisTick": {"show": False},
                    "splitLine": {"length": 12, "lineStyle": {"width": 2, "color": "#999"}},
                    "axisLabel": {"distance": 25, "color": "#999", "fontSize": 12},
                    "anchor": {"show": True, "showAbove": True, "size": 18, "itemStyle": {"borderWidth": 10}},
                    "title": {"show": True, "offsetCenter": [0, "-20%"], "fontSize": 16},
                    "detail": {"valueAnimation": True, "offsetCenter": [0, "20%"], "fontSize": 28, "fontWeight": "bolder", "formatter": "{value}%", "color": gauge_color},
                    "data": [{"value": risk_score, "name": "Churn Risk"}],
                }]
            }
            st_echarts(options=opt_gauge, height="280px")

            if risk_score > 60:
                st.error("High Risk Profile: Proactive customer retention intervention required.")
            else:
                st.success("Low Risk Profile: Standard customer account status.")

    # ==========================================
    # TAB 4: RAW DATA
    # ==========================================
    with tab4:
        st.subheader("Filtered Dataset")
        st.markdown(f"Displaying **{len(df)}** records based on active filters.")

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_data,
            file_name="filtered_ecommerce_churn_data.csv",
            mime="text/csv",
        )

        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.warning("Ensure `clean_data.csv` is located at `data/processed/clean_data.csv`.")
    st.error(f"Error Details: {e}")