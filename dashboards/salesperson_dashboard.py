import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def show(df):
    st.subheader("👤 Salesperson Dashboard")

    # -----------------------------
    # 🔍 FILTERS
    # -----------------------------
    f1, f2, f3 = st.columns(3)

    with f1:
        region = st.selectbox("Region", ["All"] + sorted(df["region"].unique()))

    with f2:
        product = st.selectbox("Product", ["All"] + sorted(df["product"].unique()))

    with f3:
        date_range = st.date_input(
            "Date Range",
            [df["date"].min(), df["date"].max()]
        )

    filtered = df.copy()

    if region != "All":
        filtered = filtered[filtered["region"] == region]

    if product != "All":
        filtered = filtered[filtered["product"] == product]

    filtered = filtered[
        (filtered["date"] >= pd.to_datetime(date_range[0])) &
        (filtered["date"] <= pd.to_datetime(date_range[1]))
    ]

    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    # -----------------------------
    # RETURN-AWARE SALES
    # -----------------------------
    filtered["net_sales"] = np.where(
        filtered["returned"] == 1, 0, filtered["sales"]
    )

    # -----------------------------
    # AGGREGATIONS
    # -----------------------------
    monthly = filtered.groupby("month")["net_sales"].sum().reset_index()
    monthly["month"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month")
    monthly["month_str"] = monthly["month"].dt.strftime("%Y-%m")

    last_6_months = monthly.tail(6)

    product_sales = filtered.groupby("product")["net_sales"].sum().reset_index()
    region_sales = filtered.groupby("region")["net_sales"].sum().reset_index()
    store_sales = filtered.groupby("storelocation")["net_sales"].sum().reset_index()

    # -----------------------------
    # KPI CALCULATIONS
    # -----------------------------
    total_orders = len(filtered)
    return_rate = (filtered["returned"].sum() / total_orders) * 100 if total_orders else 0
    net_sales = filtered["net_sales"].sum()
    avg_monthly_sales = monthly["net_sales"].mean()

    customer_kpi = (
        filtered.groupby("customer_type")
        .size()
        .reset_index(name="count")
    )

    new_customers = customer_kpi.loc[
        customer_kpi["customer_type"] == "New Customer", "count"
    ].sum()

    repeat_customers = customer_kpi.loc[
        customer_kpi["customer_type"] == "Repeat Customer", "count"
    ].sum()

    # -----------------------------
    # 📊 KPI SECTION (INCLUDING CUSTOMER KPIs)
    # -----------------------------
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        with st.container(border=True):
            st.metric("Avg Monthly Net Sales", f"{avg_monthly_sales:,.0f}")

    with k2:
        with st.container(border=True):
            st.metric("Net Sales", f"{net_sales:,.0f}")

    with k3:
        with st.container(border=True):
            st.metric("Return Rate (%)", f"{return_rate:.2f}%")

    with k4:
        with st.container(border=True):
            st.metric("Total Orders", total_orders)

    k5, k6, k7, k8 = st.columns(4)

    with k5:
        with st.container(border=True):
            st.metric("New Customers", int(new_customers))

    with k6:
        with st.container(border=True):
            st.metric("Repeat Customers", int(repeat_customers))

    with k7:
        with st.container(border=True):
            ratio = (
                repeat_customers / new_customers
                if new_customers > 0 else repeat_customers
            )
            st.metric("Repeat : New Ratio", f"{ratio:.2f}")

    with k8:
        with st.container(border=True):
            st.metric("Active Months", monthly.shape[0])

    # -----------------------------
    # 📌 GRID 1 (2×2)
    # -----------------------------
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            fig1 = px.line(
                monthly,
                x="month_str",
                y="net_sales",
                title="Monthly Net Sales Trend",
                template="plotly_dark",
                markers=True
            )
            st.plotly_chart(fig1, use_container_width=True)

    with c2:
        with st.container(border=True):
            fig2 = px.bar(
                product_sales,
                x="product",
                y="net_sales",
                title="Net Sales by Product",
                template="plotly_dark"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # 📌 GRID 2 (2×2)
    # -----------------------------
    c3, c4 = st.columns(2)

    with c3:
        with st.container(border=True):
            fig3 = px.bar(
                region_sales,
                x="region",
                y="net_sales",
                title="Net Sales by Region",
                template="plotly_dark"
            )
            st.plotly_chart(fig3, use_container_width=True)

    with c4:
        with st.container(border=True):
            fig4 = px.pie(
                filtered.groupby("customer_type")
                .size()
                .reset_index(name="count"),
                names="customer_type",
                values="count",
                title="Repeat vs New Customers",
                template="plotly_dark"
            )
            st.plotly_chart(fig4, use_container_width=True)

    # -----------------------------
    # 📊 LAST 6 MONTHS SALES (BAR CHART)
    # -----------------------------
    st.subheader("📊 Last 6 Months Net Sales")

    with st.container(border=True):
        fig5 = px.bar(
            last_6_months,
            x="month_str",
            y="net_sales",
            title="Last 6 Months Net Sales Trend",
            template="plotly_dark"
        )
        st.plotly_chart(fig5, use_container_width=True)

    # -----------------------------
    # 📍 STORE LOCATION PERFORMANCE
    # -----------------------------
    st.subheader("📍 Store Location Performance")

    with st.container(border=True):
        fig6 = px.bar(
            store_sales,
            x="storelocation",
            y="net_sales",
            title="Net Sales by Store Location",
            template="plotly_dark"
        )
        st.plotly_chart(fig6, use_container_width=True)
