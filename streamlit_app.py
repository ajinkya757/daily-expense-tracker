import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Expense Tracker", layout="centered")

# File to store data
DATA_FILE = "expenses.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Amount", "Description", "Spent By"])

# --- UI ELEMENTS ---
st.title("💰 Daily Expense Logger")

with st.form("expense_form", clear_on_submit=True):
    amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
    description = st.text_input("What was this for?")
    
    # The requested feature: Radio buttons for selection
    spent_by = st.radio("Who spent this?", options=["Ajinkya", "Komal"], horizontal=True)
    
    submitted = st.form_submit_button("Record Expense")

if submitted:
    if amount > 0 and description:
        new_data = pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Amount": [amount],
            "Description": [description],
            "Spent By": [spent_by]
        })
        
        df = load_data()
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"Recorded ₹{amount} for {spent_by}!")
    else:
        st.error("Please enter a valid amount and description.")

# --- DISPLAY HISTORY ---
st.divider()
st.subheader("Recent Expenses")
df_display = load_data()

if not df_display.empty:
    # Show summary
    totals = df_display.groupby("Spent By")["Amount"].sum()
    col1, col2 = st.columns(2)
    col1.metric("Ajinkya Total", f"₹{totals.get('Ajinkya', 0):.2f}")
    col2.metric("Komal Total", f"₹{totals.get('Komal', 0):.2f}")
    
    st.dataframe(df_display.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info("No expenses recorded yet.")
