# dashboards/admin_dashboard.py

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def show(df):
    st.subheader("⚙️ Admin Dashboard")

    # =========================================================
    # COMMON PREPARATION
    # =========================================================
    df = df.copy()
    df["net_sales"] = np.where(df["returned"] == 1, 0, df["sales"])

    monthly = df.groupby("month")["net_sales"].sum().reset_index()
    monthly["month"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month")
    monthly["month_str"] = monthly["month"].dt.strftime("%Y-%m")

    region_sales = df.groupby("region")["net_sales"].sum().reset_index()
    product_sales = df.groupby("product")["net_sales"].sum().reset_index()

    # =========================================================
    # KPIs (SYSTEM LEVEL)
    # =========================================================
    total_net_sales = df["net_sales"].sum()
    total_orders = df.shape[0]
    return_rate = df["returned"].mean() * 100
    repeat_pct = (
        df[df["customer_type"] == "Repeat Customer"].shape[0]
        / df.shape[0]
    ) * 100
    total_customers = df["customername"].nunique()

    # =========================================================
    # TABS
    # =========================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Data Overview",
        "👔 Manager Comparison",
        "👤 Salesperson Comparison",
        "🔎 Manager Drill-down",
        "🔎 Salesperson Drill-down"
    ])

    # =========================================================
    # TAB 1: DATA OVERVIEW (UNCHANGED)
    # =========================================================
    with tab1:

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1: st.container(border=True).metric("Total Net Sales", f"{total_net_sales:,.0f}")
        with k2: st.container(border=True).metric("Total Orders", total_orders)
        with k3: st.container(border=True).metric("Return Rate (%)", f"{return_rate:.2f}%")
        with k4: st.container(border=True).metric("Repeat Customer %", f"{repeat_pct:.2f}%")
        with k5: st.container(border=True).metric("Unique Customers", total_customers)

        c1, c2 = st.columns(2)
        with c1:
            st.container(border=True).plotly_chart(
                px.line(monthly, x="month_str", y="net_sales",
                        title="System Monthly Net Sales Trend",
                        template="plotly_dark", markers=True),
                use_container_width=True
            )
        with c2:
            st.container(border=True).plotly_chart(
                px.bar(region_sales, x="region", y="net_sales",
                       title="Net Sales by Region",
                       template="plotly_dark"),
                use_container_width=True
            )

        c3, c4 = st.columns(2)
        with c3:
            st.container(border=True).plotly_chart(
                px.bar(product_sales, x="product", y="net_sales",
                       title="Net Sales by Product",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c4:
            st.container(border=True).plotly_chart(
                px.pie(
                    df.groupby("customer_type").size().reset_index(name="count"),
                    names="customer_type", values="count",
                    title="Customer Type Distribution",
                    template="plotly_dark"
                ),
                use_container_width=True
            )

        st.subheader("📄 Raw Data")
        st.container(border=True).dataframe(df, use_container_width=True)

    # =========================================================
    # TAB 2: MANAGER COMPARISON (UNCHANGED)
    # =========================================================
    with tab2:

        mgr_group = df.groupby("regionmanager")

        mgr_df = pd.DataFrame({
            "Total Net Sales": mgr_group["net_sales"].sum(),
            "Avg Net Sales": mgr_group["net_sales"].mean(),
            "Return Rate %": mgr_group["returned"].mean() * 100,
            "Repeat Customer %": (
                df[df["customer_type"] == "Repeat Customer"]
                .groupby("regionmanager").size()
                / mgr_group.size()
            ) * 100
        }).reset_index()

        st.container(border=True).dataframe(mgr_df, use_container_width=True)

        c5, c6 = st.columns(2)
        with c5:
            st.container(border=True).plotly_chart(
                px.bar(mgr_df, x="regionmanager", y="Total Net Sales",
                       title="Total Net Sales by Manager",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c6:
            st.container(border=True).plotly_chart(
                px.bar(mgr_df, x="regionmanager", y="Repeat Customer %",
                       title="Repeat Customer % by Manager",
                       template="plotly_dark"),
                use_container_width=True
            )

    # =========================================================
    # TAB 3: SALESPERSON COMPARISON (UNCHANGED)
    # =========================================================
    with tab3:

        sp_group = df.groupby("salesperson")

        sp_df = pd.DataFrame({
            "Total Net Sales": sp_group["net_sales"].sum(),
            "Avg Net Sales": sp_group["net_sales"].mean(),
            "Return Rate %": sp_group["returned"].mean() * 100,
            "Repeat Customer %": (
                df[df["customer_type"] == "Repeat Customer"]
                .groupby("salesperson").size()
                / sp_group.size()
            ) * 100
        }).reset_index()

        st.container(border=True).dataframe(sp_df, use_container_width=True)

        c7, c8 = st.columns(2)
        with c7:
            st.container(border=True).plotly_chart(
                px.bar(sp_df, x="salesperson", y="Total Net Sales",
                       title="Total Net Sales by Salesperson",
                       template="plotly_dark"),
                use_container_width=True
            )
        with c8:
            st.container(border=True).plotly_chart(
                px.bar(sp_df, x="salesperson", y="Repeat Customer %",
                       title="Repeat Customer % by Salesperson",
                       template="plotly_dark"),
                use_container_width=True
            )

    # =========================================================
    # TAB 4: MANAGER DRILL-DOWN (NEW)
    # =========================================================
    with tab4:

        mgr = st.selectbox("Select Manager", sorted(df["regionmanager"].unique()))
        mgr_df = df[df["regionmanager"] == mgr]

        mgr_monthly = mgr_df.groupby("month")["net_sales"].sum().reset_index()
        mgr_monthly["month"] = pd.to_datetime(mgr_monthly["month"])
        mgr_monthly = mgr_monthly.sort_values("month")
        mgr_monthly["month_str"] = mgr_monthly["month"].dt.strftime("%Y-%m")

        st.container(border=True).plotly_chart(
            px.line(mgr_monthly, x="month_str", y="net_sales",
                    title=f"{mgr} – Monthly Net Sales",
                    template="plotly_dark", markers=True),
            use_container_width=True
        )

        st.container(border=True).plotly_chart(
            px.bar(
                mgr_df.groupby("salesperson")["net_sales"].sum().reset_index(),
                x="salesperson", y="net_sales",
                title=f"{mgr} – Sales by Salesperson",
                template="plotly_dark"
            ),
            use_container_width=True
        )

    # =========================================================
    # TAB 5: SALESPERSON DRILL-DOWN (NEW – FULL VIEW)
    # =========================================================
    with tab5:

        sp = st.selectbox("Select Salesperson", sorted(df["salesperson"].unique()))
        sp_df = df[df["salesperson"] == sp]

        sp_monthly = sp_df.groupby("month")["net_sales"].sum().reset_index()
        sp_monthly["month"] = pd.to_datetime(sp_monthly["month"])
        sp_monthly = sp_monthly.sort_values("month")
        sp_monthly["month_str"] = sp_monthly["month"].dt.strftime("%Y-%m")

        st.container(border=True).plotly_chart(
            px.line(sp_monthly, x="month_str", y="net_sales",
                    title=f"{sp} – Monthly Net Sales",
                    template="plotly_dark", markers=True),
            use_container_width=True
        )

        st.container(border=True).plotly_chart(
            px.bar(
                sp_df.groupby("product")["net_sales"].sum().reset_index(),
                x="product", y="net_sales",
                title=f"{sp} – Net Sales by Product",
                template="plotly_dark"
            ),
            use_container_width=True
        )

        st.container(border=True).plotly_chart(
            px.pie(
                sp_df.groupby("customer_type").size().reset_index(name="count"),
                names="customer_type", values="count",
                title=f"{sp} – Repeat vs New Customers",
                template="plotly_dark"
            ),
            use_container_width=True
        )
