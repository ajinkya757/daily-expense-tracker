import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Permanent Expense Tracker", layout="centered")

# Establish Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Clear cache to ensure we see the latest data
    return conn.read(ttl=0) 

st.title("💰 Permanent Expense Logger")

tab1, tab2 = st.tabs(["📝 Add Expense", "🔍 View History"])

with tab1:
    with st.form("expense_form", clear_on_submit=True):
        expense_date = st.date_input("Date", value=datetime.now().date())
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        description = st.text_input("Description")
        spent_by = st.radio("Who spent this?", options=["Ajinkya", "Komal"], horizontal=True)
        submitted = st.form_submit_button("Save to Google Sheets")

    if submitted:
        if amount > 0 and description:
            # Prepare the new row
            new_row = pd.DataFrame({
                "Date": [expense_date.strftime('%d/%m/%Y')],
                "Amount": [amount],
                "Description": [description],
                "Spent By": [spent_by]
            })
            
            # Load existing data
            existing_data = load_data()
            
            # Combine and update the entire sheet
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            try:
                # This writes the updated table back to your Sheet
                conn.update(data=updated_df)
                st.success(f"Recorded ₹{amount} for {spent_by} successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving to Google Sheets: {e}")
                st.info("Check if your Google Sheet is shared with 'Anyone with the link' as 'Editor'.")
        else:
            st.warning("Please enter both an amount and a description.")

with tab2:
    df = load_data()
    if not df.empty:
        # Convert date for filtering and sorting
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', dayfirst=True)
        
        months = df['Date'].dt.strftime('%B %Y').unique().tolist()
        sel_month = st.selectbox("Filter Month", options=["All"] + months)
        
        disp_df = df.copy()
        if sel_month != "All":
            disp_df = df[df['Date'].dt.strftime('%B %Y') == sel_month]
        
        # Display cleanup
        disp_df = disp_df.sort_values(by="Date", ascending=False)
        disp_df['Date'] = disp_df['Date'].dt.strftime('%d/%m/%Y')
        disp_df.insert(0, 'Sr.No.', range(1, len(disp_df) + 1))
        
        st.dataframe(disp_df, use_container_width=True, hide_index=True)
    else:
        st.info("No data found. Add your first expense in the 'Add Expense' tab!")
