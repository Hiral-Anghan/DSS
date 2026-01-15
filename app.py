# ==========================================
# Sales Performance DSS
# Streamlit + Plotly (Power BI Style)
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(
    page_title="Sales Performance DSS",
    layout="wide"
)

# ------------------------------------------
# LOAD DATA
# ------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Product-Sales-Region.xlsx")
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df = df.dropna().drop_duplicates()

    # Derived fields
    df["sales"] = df["quantity"] * df["unitprice"]
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["salesperson"] = df["regionmanager"]

    # Target (synthetic)
    df["target"] = df["sales"] * 1.10
    df["target_achievement_pct"] = (df["sales"] / df["target"]) * 100

    return df

df = load_data()

# ------------------------------------------
# SIDEBAR FILTERS (POWER BI STYLE)
# ------------------------------------------
st.sidebar.title("🔎 Filters")

role = st.sidebar.selectbox(
    "User Role",
    ["Salesperson", "Supervisor", "Manager", "Admin"]
)

regions = st.sidebar.multiselect(
    "Region",
    options=df["region"].unique(),
    default=df["region"].unique()
)

products = st.sidebar.multiselect(
    "Product",
    options=df["product"].unique(),
    default=df["product"].unique()
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["date"].min(), df["date"].max()]
)

# ------------------------------------------
# FILTER DATA
# ------------------------------------------
filtered_df = df[
    (df["region"].isin(regions)) &
    (df["product"].isin(products)) &
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1]))
]

# Role-based filtering
if role == "Salesperson":
    filtered_df = filtered_df[
        filtered_df["salesperson"] == filtered_df["salesperson"].iloc[0]
    ]

elif role == "Supervisor":
    filtered_df = filtered_df[
        filtered_df["region"] == filtered_df["region"].iloc[0]
    ]

# ------------------------------------------
# KPI CARDS
# ------------------------------------------
st.title("📊 Sales Performance Decision Support System")

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    "Total Sales",
    f"{filtered_df['sales'].sum():,.0f}"
)

kpi2.metric(
    "Total Target",
    f"{filtered_df['target'].sum():,.0f}"
)

kpi3.metric(
    "Avg Target Achievement %",
    f"{filtered_df['target_achievement_pct'].mean():.2f}%"
)

# ------------------------------------------
# CHARTS
# ------------------------------------------
col1, col2 = st.columns(2)

with col1:
    fig_region = px.bar(
        filtered_df.groupby("region", as_index=False)["sales"].sum(),
        x="region",
        y="sales",
        title="Sales by Region"
    )
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    fig_trend = px.line(
        filtered_df.groupby("month", as_index=False)["sales"].sum(),
        x="month",
        y="sales",
        title="Sales Trend"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

fig_product = px.bar(
    filtered_df.groupby("product", as_index=False)["sales"].sum(),
    x="product",
    y="sales",
    title="Sales by Product"
)

st.plotly_chart(fig_product, use_container_width=True)

# ------------------------------------------
# ADMIN DATA VIEW
# ------------------------------------------
if role == "Admin":
    st.subheader("📋 Detailed Data View")
    st.dataframe(filtered_df)

