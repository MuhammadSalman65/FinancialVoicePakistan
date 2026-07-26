import streamlit as st
import pandas as pd
import sys, os, importlib
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, add_transaction, get_all_transactions, get_setting

st.set_page_config(page_title="Remittance Tracker | Financial Voice", layout="wide")
init_db()

# Security Check
saved_pin = get_setting('user_pin', None)
if saved_pin and not st.session_state.get('authenticated', False):
    st.warning("Security PIN required. Please authenticate from the main page.")
    st.stop()

# Header
st.markdown("""
    <style>
    .header-banner {
        background: #0f172a;
        padding: 22px 28px;
        border-radius: 12px;
        color: #ffffff;
        border-bottom: 3px solid #0284c7;
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .header-sub {
        color: #38bdf8;
        font-size: 13px;
        margin-top: 4px;
        font-weight: 500;
    }
    </style>
    <div class="header-banner">
        <div class="header-title">Overseas Remittance Tracking & Conversion Engine</div>
        <div class="header-sub">Foreign Currency Inflows, PKR Conversion & Income Share Analysis</div>
    </div>
""", unsafe_allow_html=True)

# Currencies and default benchmark exchange rates (to PKR)
CURRENCY_RATES = {
    "GBP (£)": 360.0,
    "USD ($)": 278.5,
    "EUR (€)": 302.0,
    "SAR (﷼)": 74.2,
    "AED (د.إ)": 75.8
}

col_in, col_out = st.columns([1, 1])

with col_in:
    with st.container(border=True):
        st.subheader("New Foreign Remittance Entry")
        sender_name = st.text_input("Sender / Source Description", value="Uncle (United Kingdom)")
        curr_selected = st.selectbox("Foreign Currency", list(CURRENCY_RATES.keys()))
        
        default_rate = CURRENCY_RATES[curr_selected]
        foreign_amount = st.number_input(f"Amount in {curr_selected.split()[0]}", value=500.0, step=50.0)
        conversion_rate = st.number_input("Exchange Rate (PKR per unit)", value=float(default_rate), step=0.5)
        
        pkr_total = foreign_amount * conversion_rate
        st.info(f"Converted Total Amount: **PKR {pkr_total:,.2f}**")

# Calculate Household Remittance Dependency Ratio
rows = get_all_transactions()
total_income_db = 0.0
remittance_income_db = 0.0

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    inc_df = df[df["Type"] == "Income"]
    total_income_db = inc_df["Amount"].sum() if not inc_df.empty else 0.0
    
    rem_df = inc_df[inc_df["Tags"].str.contains("#remittance", case=False, na=False)]
    remittance_income_db = rem_df["Amount"].sum() if not rem_df.empty else 0.0

dep_ratio = (remittance_income_db / total_income_db * 100) if total_income_db > 0 else 0.0

with col_out:
    with st.container(border=True):
        st.subheader("Remittance Dependency Analytics")
        st.metric("Total Remittance Income Recorded", f"Rs. {remittance_income_db:,.0f}")
        st.metric("Household Income Share (% Remittance)", f"{dep_ratio:.1f}%")
        
        if dep_ratio > 50.0:
            st.warning("High Remittance Dependency: Over 50% of total household income relies on foreign transfers.")
        else:
            st.success("Balanced Inflow: Foreign remittance constitutes a stable proportion of total household revenue.")

        st.markdown("---")
        st.markdown("#### **Post to Central Ledger**")
        if st.button("Post Remittance Income to Database", use_container_width=True):
            add_transaction(
                date=datetime.now().strftime("%Y-%m-%d"),
                amount=pkr_total,
                category="Salary",
                description=f"Foreign Remittance ({curr_selected}): {sender_name}",
                trans_type="Income",
                tags="#remittance #foreign_inflow"
            )
            st.success(f"Successfully posted PKR {pkr_total:,.2f} to Central Ledger as Income!")
            st.rerun()