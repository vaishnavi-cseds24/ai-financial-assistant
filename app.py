import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import ollama
import datetime
import calendar
@st.cache_data

def ask_ai_local(user_input, df, budget, current_day, total_days):
    if df.empty:
        return "No expense data available yet."

    total = df["Amount"].sum()
    remaining = budget - total

    category_sum = df.groupby("Category")["Amount"].sum().to_dict()
    category_text = "\n".join([f"{k}: ₹{v:.2f}" for k, v in category_sum.items()])

    avg_daily_spend = total / current_day if current_day > 0 else 0
    projected_total = avg_daily_spend * total_days

    prompt = f"""
You are a smart financial advisor.

User's financial data:
- Monthly budget: ₹{budget:.2f}
- Total spent so far: ₹{total:.2f}
- Day of month: {current_day} out of {total_days}
- Average daily spend: ₹{avg_daily_spend:.2f}
- Projected monthly spending: ₹{projected_total:.2f}

Category breakdown:
{category_text}

Your job:
- Analyze if the user is on track
- Predict overspending if trends continue
- Give smart, practical advice
- Mention time context (early/mid/late month)

User question:
{user_input}

Answer:
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]





st.set_page_config(page_title="AI Financial Assistant", layout="wide")

st.title("AI Financial Assistant")
st.caption("Track. Analyze. Improve your spending habits.")

DATA_FILE = "expenses.csv"


if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Description", "Category", "Amount"])
    df.to_csv(DATA_FILE, index=False)


st.sidebar.header("Add Expense")

description = st.sidebar.text_input("Description")

category = st.sidebar.selectbox(
    "Category",
    ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
)

amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, format="%.2f")
budget = st.sidebar.number_input("Monthly Budget (₹)", min_value=0.0, value=5000.0)
df = pd.read_csv(DATA_FILE)
today = datetime.date.today()
current_day = today.day
total_days = calendar.monthrange(today.year, today.month)[1]

days_left = total_days - current_day

if st.sidebar.button("Add Expense"):
    
    new_expense = pd.DataFrame({
    "Description": [description],
    "Category": [category],
    "Amount": [amount]
})

    df = pd.concat([df, new_expense], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    st.sidebar.success("Expense Added Successfully!")




col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Total Spending")
    st.metric("Total Spent", f"₹ {df['Amount'].sum():,.2f}")
    total = df["Amount"].sum()
    st.write(f"💼 Budget: ₹{budget:,.2f}")

    if total > budget:
        st.error("🚨 You have exceeded your monthly budget!")
    elif total > 0.8 * budget:
        st.warning("⚠️ You are close to your budget limit!")
    else:
        st.success("✅ You are within your budget.")

with col2:
    st.subheader("📄 Recent Expenses")
    st.dataframe(df.tail())
    st.subheader("🗑 Delete an Expense")
expense_index = st.number_input(
    "Enter the index of the expense you want to delete",
    min_value=0,
    max_value=len(df)-1,
    step=1
)

if st.button("Delete Expense"):

    df = df.drop(expense_index)
    df = df.reset_index(drop=True)
    df.to_csv("expenses.csv", index=False)

    st.success("Expense deleted successfully!")
    st.subheader("📈 Spending by Category")

    
    category_summary = df.groupby("Category")["Amount"].sum()

    st.write(category_summary)

    st.bar_chart(category_summary)

    if not df.empty:
        if st.button("💡 Generate AI Insight"):
            insight = ask_ai_local("Give a short financial insight", df, budget, current_day, total_days)
            st.info(insight)

    

st.subheader("📈 Spending Trend")
if not df.empty:
    st.line_chart(df["Amount"])
total = df["Amount"].sum()

if total > 5000:
    st.warning("⚠️ Your spending is high this month!")
else:
    st.success("✅ Your spending is under control!")


st.subheader("🗑 Delete an Expense")


df_display = df.reset_index(drop=False)  

st.dataframe(df_display)

selected_index = st.selectbox(
    "Select the expense to delete (by index)",
    df_display.index  
)

if st.button("Delete Expense"):
    df = df.drop(selected_index)
    df = df.reset_index(drop=True)
    df.to_csv(DATA_FILE, index=False)

    st.success("Expense deleted successfully!")
    st.rerun()



st.subheader("🤖 AI Financial Assistant")

st.caption("Try: 'Where am I overspending?', 'Give me advice', 'How can I save money?'")

user_input = st.text_input("Ask something about your spending:")

if user_input:
    response = ask_ai_local(user_input, df, budget, current_day, total_days)
    st.markdown(f"**🤖 AI Assistant:** {response}")        