import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AI Financial Assistant", layout="wide")

st.title("AI Financial Assistant")
st.caption("Track. Analyze. Improve your spending habits.")

DATA_FILE = "expenses.csv"

# Create CSV if not exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Description", "Amount"])
    df.to_csv(DATA_FILE, index=False)

# Sidebar input
st.sidebar.header("Add Expense")

description = st.sidebar.text_input("Description")

category = st.sidebar.selectbox(
    "Category",
    ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
)

amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, format="%.2f")
df = pd.read_csv(DATA_FILE)

if st.sidebar.button("Add Expense"):
    
    new_expense = pd.DataFrame({
    "Description": [description],
    "Category": [category],
    "Amount": [amount]
})

    df = pd.concat([df, new_expense], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    st.sidebar.success("Expense Added Successfully!")

# Load data


col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Total Spending")
    st.metric("Total Spent", f"₹ {df['Amount'].sum():,.2f}")

with col2:
    st.subheader("📄 Recent Expenses")
    st.dataframe(df.tail())
    st.subheader("📈 Spending by Category")

    category_summary = df.groupby("Category")["Amount"].sum().reset_index()
    st.dataframe(category_summary)

    st.bar_chart(category_summary.set_index("Category"))

st.subheader("📈 Spending Trend")
if not df.empty:
    st.line_chart(df["Amount"])