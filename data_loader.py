import pandas as pd
import streamlit as st

@st.cache_data
def load_users():
    df = pd.read_excel("users.xlsx")
    df.columns = df.columns.str.lower()
    return df

@st.cache_data
def load_sales():
    df = pd.read_excel("Product-Sales-Region.xlsx")
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df = df.dropna().drop_duplicates()

    df["sales"] = df["quantity"] * df["unitprice"]
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    return df
