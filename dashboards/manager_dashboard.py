# dashboards/manager_dashboard.py

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def show(df):
    st.subheader("👥 Manager Dashboard")

    # =========================================================
    # FILTERS (APPLY TO ALL TABS)
    # =========================================================
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

    # =========================================================
    # COMMON PREPARATION
    # =========================================================
    filtered["net_sales"] = np.where(filtered["returned"] == 1, 0, filtered["sales"])

    monthly = filtered.groupby("month")["net_sales"].sum().reset_index()
    monthly["month"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month")
    monthly["month_str"] = monthly["month"].dt.strftime("%Y-%m")
    last_6_months = monthly.tail(6)

    region_sales = filtered.groupby("region")["net_sales"].sum().reset_index()
    product_sales = filtered.groupby("product")["net_sales"].sum().reset_index()
    store_sales = filtered.groupby("storelocation")["net_sales"].sum().reset_index()

    return_by_region = (
        filtered.groupby("region")["returned"]
        .mean()
        .reset_index(name="return_rate")
    )
    return_by_region["return_rate"] *= 100

    # =========================================================
    # KPI VALUES
    # =========================================================
    total_net_sales = filtered["net_sales"].sum()
    avg_monthly_net_sales = monthly["net_sales"].mean()
    return_rate = filtered["returned"].mean() * 100
    repeat_pct = (
        filtered[filtered["customer_type"] == "Repeat Customer"].shape[0]
        / filtered.shape[0]
    ) * 100

    best_region = region_sales.sort_values("net_sales", ascending=False).iloc[0]["region"]
    worst_region = region_sales.sort_values("net_sales", ascending=True).iloc[0]["region"]

    top_product = product_sales.sort_values("net_sales", ascending=False).iloc[0]["product"]
    worst_product = product_sales.sort_values("net_sales", ascending=True).iloc[0]["product"]

    # =========================================================
    # TABS
    # =========================================================
    tab1, tab2, tab3 = st.tabs([
        "📊 Overview",
        "👤 Salesperson Performance",
        "🔎 Salesperson Drill-down"
    ])

    # =========================================================
    # TAB 1: OVERVIEW (APPENDED KPIs ONLY)
    # =========================================================
    with tab1:

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.container(border=True).metric("Total Net Sales", f"{total_net_sales:,.0f}")
        with k2: st.container(border=True).metric("Avg Monthly Net Sales", f"{avg_monthly_net_sales:,.0f}")
        with k3: st.container(border=True).metric("Return Rate (%)", f"{return_rate:.2f}%")
        with k4: st.container(border=True).metric("Repeat Customer %", f"{repeat_pct:.2f}%")

        k5, k6, k7, k8 = st.columns(4)
        with k5: st.container(border=True).metric("Best Region", best_region)
        with k6: st.container(border=True).metric("Worst Region", worst_region)
        with k7: st.container(border=True).metric("Top Product", top_product)
        with k8: st.container(border=True).metric("Worst Product", worst_product)

        # --- EXISTING CHARTS (UNCHANGED) ---
        c1, c2 = st.columns(2)
        with c1:
            st.container(border=True).plotly_chart(
                px.line(monthly, x="month_str", y="net_sales",
                        title="Monthly Net Sales Trend",
                        template="plotly_dark", markers=True),
                use_container_width=True
            )
        with c2:
            st.container(border=True).plotly_chart(
                px.bar(last_6_months, x="month_str", y="net_sales",
                       title="Last 6 Months Net Sales",
                       template="plotly_dark"),
                use_container_width=True
            )

        c3, c4 = st.columns(2)
        with c3:
            st.container(border=True).plotly_chart(
                px.bar(region_sales, x="region", y="net_sales",
                       title="Net Sales by Region",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c4:
            st.container(border=True).plotly_chart(
                px.bar(product_sales, x="product", y="net_sales",
                       title="Net Sales by Product",
                       template="plotly_dark"),
                use_container_width=True
            )

        c5, c6 = st.columns(2)
        with c5:
            st.container(border=True).plotly_chart(
                px.bar(return_by_region, x="region", y="return_rate",
                       title="Return Rate by Region (%)",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c6:
            st.container(border=True).plotly_chart(
                px.pie(
                    filtered.groupby("customer_type")
                    .size().reset_index(name="count"),
                    names="customer_type", values="count",
                    title="Customer Type Distribution",
                    template="plotly_dark"
                ),
                use_container_width=True
            )

        c7, c8 = st.columns(2)
        with c7:
            st.container(border=True).plotly_chart(
                px.bar(product_sales.sort_values("net_sales", ascending=False).head(5),
                       x="product", y="net_sales",
                       title="Top 5 Products",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c8:
            st.container(border=True).plotly_chart(
                px.bar(store_sales, x="storelocation", y="net_sales",
                       title="Net Sales by Store Location",
                       template="plotly_dark"),
                use_container_width=True
            )

    # =========================================================
    # TAB 2: SALESPERSON PERFORMANCE (APPENDED CHARTS)
    # =========================================================
    with tab2:

        sp_group = filtered.groupby("salesperson")

        sp_df = pd.DataFrame({
            "Total Net Sales": sp_group["net_sales"].sum(),
            "Avg Net Sales": sp_group["net_sales"].mean(),
            "Return Rate %": sp_group["returned"].mean() * 100,
            "Repeat Customer %": (
                filtered[filtered["customer_type"] == "Repeat Customer"]
                .groupby("salesperson").size()
                / sp_group.size()
            ) * 100
        }).reset_index()

        st.container(border=True).dataframe(sp_df, use_container_width=True)

        c9, c10 = st.columns(2)
        with c9:
            st.container(border=True).plotly_chart(
                px.bar(sp_df, x="salesperson", y="Total Net Sales",
                       title="Total Net Sales by Salesperson",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c10:
            st.container(border=True).plotly_chart(
                px.bar(sp_df, x="salesperson", y="Repeat Customer %",
                       title="Repeat Customer % by Salesperson",
                       template="plotly_dark"),
                use_container_width=True
            )

        # --- NEW CONTRIBUTION CHARTS ---
        c11, c12 = st.columns(2)

        with c11:
            st.container(border=True).plotly_chart(
                px.bar(
                    filtered.groupby(["product", "salesperson"])["net_sales"]
                    .sum().reset_index(),
                    x="product", y="net_sales", color="salesperson",
                    title="Product-wise Salesperson Contribution",
                    template="plotly_dark"
                ),
                use_container_width=True
            )

        with c12:
            st.container(border=True).plotly_chart(
                px.bar(
                    filtered.groupby(["region", "salesperson"])["net_sales"]
                    .sum().reset_index(),
                    x="region", y="net_sales", color="salesperson",
                    title="Region-wise Salesperson Contribution",
                    template="plotly_dark"
                ),
                use_container_width=True
            )

    # =========================================================
    # TAB 3: SALESPERSON DRILL-DOWN (FULL SALESPERSON VIEW)
    # =========================================================
    with tab3:

        sp = st.selectbox("Select Salesperson", sorted(filtered["salesperson"].unique()))
        sp_df = filtered[filtered["salesperson"] == sp]

        sp_df["net_sales"] = np.where(sp_df["returned"] == 1, 0, sp_df["sales"])

        sp_monthly = sp_df.groupby("month")["net_sales"].sum().reset_index()
        sp_monthly["month"] = pd.to_datetime(sp_monthly["month"])
        sp_monthly = sp_monthly.sort_values("month")
        sp_monthly["month_str"] = sp_monthly["month"].dt.strftime("%Y-%m")
        last_6 = sp_monthly.tail(6)

        avg_monthly = sp_monthly["net_sales"].mean()
        return_rate_sp = sp_df["returned"].mean() * 100
        repeat_pct_sp = (
            sp_df[sp_df["customer_type"] == "Repeat Customer"].shape[0]
            / sp_df.shape[0]
        ) * 100
        total_net_sp = sp_df["net_sales"].sum()

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.container(border=True).metric("Avg Monthly Net Sales", f"{avg_monthly:,.0f}")
        with k2: st.container(border=True).metric("Return Rate (%)", f"{return_rate_sp:.2f}%")
        with k3: st.container(border=True).metric("Repeat Customer %", f"{repeat_pct_sp:.2f}%")
        with k4: st.container(border=True).metric("Total Net Sales", f"{total_net_sp:,.0f}")

        c13, c14 = st.columns(2)
        with c13:
            st.container(border=True).plotly_chart(
                px.line(sp_monthly, x="month_str", y="net_sales",
                        title=f"{sp} – Monthly Net Sales Trend",
                        template="plotly_dark", markers=True),
                use_container_width=True
            )
        with c14:
            st.container(border=True).plotly_chart(
                px.bar(last_6, x="month_str", y="net_sales",
                       title=f"{sp} – Last 6 Months Net Sales",
                       template="plotly_dark"),
                use_container_width=True
            )

        c15, c16 = st.columns(2)
        with c15:
            st.container(border=True).plotly_chart(
                px.bar(sp_df.groupby("product")["net_sales"].sum().reset_index(),
                       x="product", y="net_sales",
                       title=f"{sp} – Net Sales by Product",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c16:
            st.container(border=True).plotly_chart(
                px.bar(sp_df.groupby("region")["net_sales"].sum().reset_index(),
                       x="region", y="net_sales",
                       title=f"{sp} – Net Sales by Region",
                       template="plotly_dark"),
                use_container_width=True
            )

        c17, c18 = st.columns(2)
        with c17:
            st.container(border=True).plotly_chart(
                px.bar(sp_df.groupby("storelocation")["net_sales"].sum().reset_index(),
                       x="storelocation", y="net_sales",
                       title=f"{sp} – Net Sales by Store Location",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c18:
            st.container(border=True).plotly_chart(
                px.pie(
                    sp_df.groupby("customer_type").size().reset_index(name="count"),
                    names="customer_type", values="count",
                    title=f"{sp} – Repeat vs New Customers",
                    template="plotly_dark"
                ),
                use_container_width=True
            )
