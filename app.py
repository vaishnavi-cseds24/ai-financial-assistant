import streamlit as st
import pandas as pd
import os
import ollama
import datetime
import calendar
import altair as alt

@st.cache_data
def ask_ai_local(user_input, df, budget, savings_goal):
    if df.empty:
        return "No expense data available yet."

    total = df["Amount"].sum()
    category_sum = df.groupby("Category")["Amount"].sum().to_dict()
    category_text = "\n".join([f"{k}: ₹{v:.2f}" for k, v in category_sum.items()])

    prompt = f"""
You are a helpful financial assistant.

User details:
- Budget: ₹{budget}
- Savings goal: ₹{savings_goal}
- Total spent: ₹{total}

Spending by category:
{category_text}

User question:
{user_input}

Instructions:
- Give a clear and complete answer
- Keep it slightly detailed (4–6 lines max)
- Give practical and relevant advice
- Do NOT cut off mid-sentence
- Do NOT invent numbers
- Do NOT repeat the input data unnecessarily
- STOP after completing the answer
"""

    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}],
        options={
            "num_predict": 300,
            "temperature": 0.3
        }
    )

    answer = response["message"]["content"].strip()

    if "cutting_off_here" in answer:
        answer = answer.split("cutting_off_here")[0]

    if not answer.endswith((".", "!", "?")):
        answer += "."

    return answer


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

budget = st.sidebar.number_input("Monthly Budget (₹)", min_value=0.0, value=10000.0)

savings_goal = st.sidebar.number_input(
    "Monthly Savings Goal (₹)",
    min_value=0.0,
    value=2000.0
)

df = pd.read_csv(DATA_FILE)

today = datetime.date.today()
current_day = today.day
total_days = calendar.monthrange(today.year, today.month)[1]

total_spent = df["Amount"].sum()
required_remaining = budget - savings_goal
remaining_budget = required_remaining - total_spent
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
    st.metric("Total Spent", f"₹ {total_spent:,.2f}")
    st.write(f"💼 Budget: ₹{budget:,.2f}")
    st.write(f"🎯 Savings Goal: ₹{savings_goal:,.2f}")
    st.write(f"💡 Max allowed spending: ₹{required_remaining:,.2f}")

    if total_spent > required_remaining:
        st.error("🚨 You are overspending! Savings goal at risk.")
    else:
        st.success("✅ You are on track to meet your savings goal!")

    st.write(f"💸 Remaining safe budget: ₹{remaining_budget:,.2f}")

with col2:
    st.subheader("📄 Recent Expenses")
    st.dataframe(df.tail())

st.subheader("🗑 Delete an Expense")

expense_index = st.number_input(
    "Enter index to delete",
    min_value=0,
    max_value=len(df)-1 if len(df) > 0 else 0,
    step=1
)

if st.button("Delete Expense"):
    df = df.drop(expense_index).reset_index(drop=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Deleted successfully!")
    st.rerun()

# ✅ Colored Bar Chart using Altair
st.subheader("📊 Spending by Category")

if not df.empty:
    category_summary = df.groupby("Category")["Amount"].sum().reset_index()

    chart = alt.Chart(category_summary).mark_bar().encode(
        x=alt.X("Category", sort="-y"),
        y="Amount",
        color="Category"
    ).properties(
        height=400
    )

    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text='Amount'
    )

    st.altair_chart(chart + text, use_container_width=True)

st.subheader("🤖 AI Financial Assistant")

st.caption("Try: 'How can I save more?', 'What should I improve?', 'Give me financial advice'")

user_input = st.text_input("Ask something about your spending:")

if user_input:
    text = user_input.lower()

    if any(word in text for word in ["daily", "per day", "each day", "how much should i spend"]):
        if days_left > 0:
            daily_limit = remaining_budget / days_left
            avg_daily_spend = total_spent / current_day if current_day > 0 else 0

            st.success(f"📅 Recommended daily spend: ₹{daily_limit:.2f}")
            st.write(f"📊 Your current daily average: ₹{avg_daily_spend:.2f}")

            if avg_daily_spend > daily_limit:
                st.error("🚨 You are currently overspending per day.")
            else:
                st.success("✅ Your daily spending is under control.")
        else:
            st.warning("Month ending. Limit spending.")

    elif "overspend" in text:
        category_sum = df.groupby("Category")["Amount"].sum()
        top_category = category_sum.idxmax()
        top_amount = category_sum.max()
        st.warning(f"⚠️ You are spending the most on **{top_category} (₹{top_amount:.2f})**.")

    elif "on track" in text:
        avg_daily_spend = total_spent / current_day if current_day > 0 else 0
        projected_spend = avg_daily_spend * total_days

        if projected_spend <= required_remaining:
            st.success("✅ You are on track based on your current spending pattern.")
        else:
            st.error("🚨 At this rate, you will overspend and miss your savings goal.")

        st.write(f"📊 Projected spending: ₹{projected_spend:.2f}")

    else:
        response = ask_ai_local(user_input, df, budget, savings_goal)
        st.markdown(f"**🤖 AI Assistant:**\n\n{response}")