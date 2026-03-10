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
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        return pd.DataFrame(columns=["Date", "Amount", "Description", "Spent By"])

# --- UI ELEMENTS ---
st.title("💰 Daily Expense Logger")

# TAB 1: Add New Expense
# TAB 2: View & Edit History
tab1, tab2 = st.tabs(["📝 Add Expense", "🔍 View & Edit History"])

with tab1:
    with st.form("expense_form", clear_on_submit=True):
        expense_date = st.date_input("Date of Expense", value=datetime.now().date())
        amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
        description = st.text_input("What was this for?")
        spent_by = st.radio("Who spent this?", options=["Ajinkya", "Komal"], horizontal=True)
        
        submitted = st.form_submit_button("Record Expense")

    if submitted and amount > 0 and description:
        new_row = pd.DataFrame({"Date": [pd.to_datetime(expense_date)], "Amount": [amount], "Description": [description], "Spent By": [spent_by]})
        df = load_data()
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"Recorded ₹{amount}!")

with tab2:
    df_display = load_data()
    if not df_display.empty:
        # Month Filter
        months = df_display['Date'].dt.strftime('%B %Y').unique().tolist()
        selected_month = st.selectbox("Filter by Month", options=["All"] + months)
        
        filtered_df = df_display.copy()
        if selected_month != "All":
            filtered_df = df_display[df_display['Date'].dt.strftime('%B %Y') == selected_month]

        # --- EDIT FEATURE ---
        st.info("💡 You can edit cells directly in the table below. To delete a row, select it and press 'Delete' on your keyboard.")
        
        # We use st.data_editor to allow live editing
        edited_df = st.data_editor(
            filtered_df.sort_values(by="Date", ascending=False),
            use_container_width=True,
            num_rows="dynamic", # Allows deleting rows
            column_config={
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "Amount": st.column_config.NumberColumn("Amount", format="₹%.2f")
            },
            hide_index=True,
            key="main_editor"
        )

        # Save Button for Edits
        if st.button("💾 Save Changes"):
            # If "All" is selected, we replace the whole file. 
            # If a month is selected, we merge back carefully.
            full_df = load_data()
            if selected_month == "All":
                edited_df.to_csv(DATA_FILE, index=False)
            else:
                # Remove old records for this month and add the edited ones
                other_months = full_df[full_df['Date'].dt.strftime('%B %Y') != selected_month]
                final_df = pd.concat([other_months, edited_df], ignore_index=True)
                final_df.to_csv(DATA_FILE, index=False)
            
            st.success("Changes saved successfully!")
            st.rerun()

        # Totals & Download
        totals = edited_df.groupby("Spent By")["Amount"].sum()
        st.write(f"**Ajinkya:** ₹{totals.get('Ajinkya', 0):.2f} | **Komal:** ₹{totals.get('Komal', 0):.2f}")
        
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download This Report", data=csv, file_name=f"Expenses_{selected_month}.csv")
    else:
        st.info("No records found.")
