import streamlit as st
import numpy as np
from data_loader import load_users, load_sales

from dashboards.salesperson_dashboard import show as salesperson_view
from dashboards.manager_dashboard import show as manager_view
from dashboards.admin_dashboard import show as admin_view

st.set_page_config(page_title="Sales DSS", layout="wide")

# ------------------------
# LOAD DATA
# ------------------------
users_df = load_users()
sales_df = load_sales()

# ------------------------
# CUSTOMER TYPE (GLOBAL LOGIC)
# ------------------------
customer_order_counts = (
    sales_df.groupby("customername")
    .size()
    .reset_index(name="order_count")
)

customer_order_counts["customer_type"] = np.where(
    customer_order_counts["order_count"] > 1,
    "Repeat Customer",
    "New Customer"
)

sales_df = sales_df.merge(
    customer_order_counts[["customername", "customer_type"]],
    on="customername",
    how="left"
)

# ------------------------
# SESSION STATE
# ------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ------------------------
# LOGIN
# ------------------------
def login():
    st.title("🔐 Login – Sales Performance DSS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        match = users_df[
            (users_df["username"] == username) &
            (users_df["password"] == password)
        ]

        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.role = match.iloc[0]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------------
# APP CONTROLLER
# ------------------------
if not st.session_state.logged_in:
    login()
else:
    role = st.session_state.role

    header_left, header_right = st.columns([4, 1])

    with header_left:
        st.title("📊 Sales Performance Decision Support System")

    with header_right:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()

    # -------- ROLE-BASED DASHBOARDS --------
    if role == "Salesperson":
        salesperson_view(sales_df)

    elif role == "Manager":
        manager_view(sales_df)

    elif role == "Admin":
        admin_view(sales_df)
