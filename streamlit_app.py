import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Expense Tracker", layout="centered")

DATA_FILE = "expenses.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Convert to datetime objects for internal logic
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        return pd.DataFrame(columns=["Date", "Amount", "Description", "Spent By"])

# --- UI ELEMENTS ---
st.title("💰 Daily Expense Logger")

with st.form("expense_form", clear_on_submit=True):
    expense_date = st.date_input("Date of Expense", value=datetime.now().date())
    amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
    description = st.text_input("What was this for?")
    spent_by = st.radio("Who spent this?", options=["Ajinkya", "Komal"], horizontal=True)
    
    submitted = st.form_submit_button("Record Expense")

if submitted:
    if amount > 0 and description:
        new_data = pd.DataFrame({
            "Date": [pd.to_datetime(expense_date)],
            "Amount": [amount],
            "Description": [description],
            "Spent By": [spent_by]
        })
        
        df = load_data()
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"Recorded ₹{amount} for {spent_by}!")

# --- DISPLAY & FILTERS ---
st.divider()
df_display = load_data()

if not df_display.empty:
    # Month-wise Filter Logic
    months = df_display['Date'].dt.strftime('%B %Y').unique().tolist()
    selected_month = st.selectbox("Filter by Month", options=["All"] + months)
    
    filtered_df = df_display.copy()
    if selected_month != "All":
        filtered_df = df_display[df_display['Date'].dt.strftime('%B %Y') == selected_month]

    filtered_df = filtered_df.sort_values(by="Date", ascending=False)
    
    # --- DATE FORMATTING FIX ---
    # Convert to DD/MM/YYYY string to remove time and match your request
    filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d/%m/%Y')
    
    # Add Sr.No.
    filtered_df.insert(0, 'Sr.No.', range(1, len(filtered_df) + 1))
    
    totals = filtered_df.groupby("Spent By")["Amount"].sum()
    col1, col2 = st.columns(2)
    col1.metric("Ajinkya Total", f"₹{totals.get('Ajinkya', 0):.2f}")
    col2.metric("Komal Total", f"₹{totals.get('Komal', 0):.2f}")
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Report as CSV",
        data=csv,
        file_name=f"Expenses_{selected_month}.csv",
        mime='text/csv',
    )
    
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
else:
    st.info("No expenses recorded yet.")
