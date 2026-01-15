# ==========================================
# Sales Performance DSS
# Streamlit + Plotly
# Login + Correct Role-Based Access
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Sales DSS", layout="wide")

# ------------------------------------------
# MOCK USER DATABASE
# (Usernames MUST match names in dataset)
# ------------------------------------------
USERS = {
    "John": {"password": "john123", "role": "Salesperson"},
    "Amit": {"password": "amit123", "role": "Salesperson"},
    "Eric": {"password": "eric123", "role": "Supervisor"},     # RegionManager
    "Sophie": {"password": "sophie123", "role": "Supervisor"},
    "Ryan": {"password": "ryan123", "role": "Supervisor"},
    "Wendy": {"password": "wendy123", "role": "Supervisor"},
    "Manager": {"password": "manager123", "role": "Manager"},
    "Admin": {"password": "admin123", "role": "Admin"}
}

# ------------------------------------------
# SESSION STATE INIT
# ------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

# ------------------------------------------
# LOGIN PAGE
# ------------------------------------------
def login_page():
    st.title("🔐 Login – Sales Performance DSS")

    left, center, right = st.columns([2, 1, 2])

    with center:
        st.markdown("### Please login to continue")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.role = USERS[username]["role"]
                st.success(f"Welcome {username} ({st.session_state.role})")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

# ------------------------------------------
# LOAD DATA
# ------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Product-Sales-Region.xlsx")
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df = df.dropna().drop_duplicates()

    # Core business fields
    df["sales"] = df["quantity"] * df["unitprice"]
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # IMPORTANT: keep both roles separate
    # salesperson column must exist in your dataset
    # regionmanager column exists as confirmed
    df["salesperson"] = df["salesperson"]
    df["region_manager"] = df["regionmanager"]

    # Synthetic target (acceptable for DSS demo)
    df["target"] = df["sales"] * 1.10
    df["target_achievement_pct"] = (df["sales"] / df["target"]) * 100

    return df

# ------------------------------------------
# DASHBOARD PAGE
# ------------------------------------------
def dashboard():
    df = load_data()
    role = st.session_state.role
    current_user = st.session_state.user

    st.title("📊 Sales Performance Decision Support System")

    # Logout
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user = None
        st.rerun()

    # --------------------------------------
    # TOP FILTERS
    # --------------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        region = st.selectbox("Region", ["All"] + sorted(df["region"].unique()))
    with c2:
        product = st.selectbox("Product", ["All"] + sorted(df["product"].unique()))
    with c3:
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

    # --------------------------------------
    # ✅ CORRECT ROLE-BASED ACCESS CONTROL
    # --------------------------------------
    if role == "Salesperson":
        # Only own sales
        filtered = filtered[filtered["salesperson"] == current_user]

    elif role == "Supervisor":
        # All regions managed by this region manager
        managed_regions = df[
            df["region_manager"] == current_user
        ]["region"].unique()
        filtered = filtered[filtered["region"].isin(managed_regions)]

    # Manager & Admin see all data

    # --------------------------------------
    # KPI CARDS
    # --------------------------------------
    avg_target = filtered["target_achievement_pct"].mean()

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Sales", f"{filtered['sales'].sum():,.0f}")
    k2.metric("Avg Target %", f"{avg_target:.2f}%")
    k3.metric("Role", role)

    # --------------------------------------
    # CHARTS
    # --------------------------------------
    c4, c5 = st.columns(2)

    with c4:
        fig1 = px.bar(
            filtered.groupby("region", as_index=False)["sales"].sum(),
            x="region",
            y="sales",
            title="Sales by Region",
            template="plotly_dark"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c5:
        fig2 = px.line(
            filtered.groupby("month", as_index=False)["sales"].sum(),
            x="month",
            y="sales",
            title="Sales Trend",
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --------------------------------------
    # ADMIN ONLY: FULL DATA ACCESS
    # --------------------------------------
    if role == "Admin":
        st.subheader("📋 Full Data Access")
        st.dataframe(filtered, use_container_width=True)

# ------------------------------------------
# MAIN CONTROLLER
# ------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
