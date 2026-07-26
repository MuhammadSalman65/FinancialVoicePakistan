import streamlit as st
import pandas as pd
import math
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Inflation Goal Planner | Financial Voice", layout="wide")
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
        background: #0f172a; padding: 22px 28px; border-radius: 12px;
        color: #ffffff; border-bottom: 3px solid #0284c7; margin-bottom: 24px;
    }
    .header-title { font-size: 24px; font-weight: 700; color: #f8fafc; margin: 0; }
    .header-sub { color: #38bdf8; font-size: 13px; margin-top: 4px; font-weight: 500; }
    </style>
    <div class="header-banner">
        <div class="header-title">Inflation-Adjusted Goal Planner & Annuity Engine</div>
        <div class="header-sub">Time Value of Money (TVM), Compounding & Target Savings Forecasting</div>
    </div>
""", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1])

with col_input:
    with st.container(border=True):
        st.subheader("Goal & TVM Configuration")
        goal_name = st.text_input("Goal Description", value="Higher Education / Asset Purchase")
        pv_target = st.number_input("Target Amount in Today's Value (Rs.)", value=500000.0, step=25000.0)
        target_months = st.number_input("Timeframe (Months)", value=24, min_value=1, max_value=120)
        annual_inflation = st.slider("Expected Annual Inflation Rate (%)", min_value=3.0, max_value=25.0, value=11.0)
        expected_investment_return = st.slider("Expected Investment Return (% p.a.)", min_value=0.0, max_value=20.0, value=8.0)

# Financial Mathematics (Time Value of Money)
years = target_months / 12.0
inflation_decimal = annual_inflation / 100.0
future_value_goal = pv_target * math.pow((1.0 + inflation_decimal), years)
inflation_loss = future_value_goal - pv_target

# Simple Monthly Saving (Cash Holding)
req_monthly_simple = future_value_goal / target_months

# TVM Sinking Fund Annuity Calculation: PMT = FV * r / ((1 + r)^n - 1)
r_monthly = (expected_investment_return / 100.0) / 12.0
if r_monthly > 0:
    pmt_annuity = (future_value_goal * r_monthly) / (math.pow(1.0 + r_monthly, target_months) - 1.0)
else:
    pmt_annuity = req_monthly_simple

# Fetch Database Actual Monthly Savings
rows = get_all_transactions()
actual_savings = 0.0
if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    total_inc = df[df["Type"] == "Income"]["Amount"].sum()
    total_exp = df[df["Type"] == "Expense"]["Amount"].sum()
    actual_savings = max(0.0, total_inc - total_exp)

with col_output:
    with st.container(border=True):
        st.subheader("Time Value of Money (TVM) Analysis")
        st.write(f"• **Goal:** {goal_name}")
        st.write(f"• **Present Target:** Rs. {pv_target:,.0f}")
        st.write(f"• **Future Inflated Target ({target_months} Months):** Rs. {future_value_goal:,.0f}")
        st.write(f"• **Purchasing Power Loss:** Rs. {inflation_loss:,.0f}")
        
        st.markdown("---")
        st.markdown("#### **Required Monthly Savings Comparison:**")
        st.write(f"• Pure Cash Holding: **Rs. {req_monthly_simple:,.0f} / month**")
        st.write(f"• Invested Strategy (@ {expected_investment_return:.1f}% return): **Rs. {pmt_annuity:,.0f} / month**")
        st.caption(f"Investing saves you **Rs. {req_monthly_simple - pmt_annuity:,.0f} / month** due to compounding returns!")
        
        st.markdown("---")
        st.markdown("#### **Ledger Status:**")
        st.write(f"• Current Recorded Net Capital: **Rs. {actual_savings:,.0f}**")
        
        if actual_savings >= pmt_annuity:
            st.success("Your recorded surplus covers the required monthly annuity investment target.")
        else:
            shortfall = pmt_annuity - actual_savings
            st.warning(f"Shortfall: Additional Rs. {shortfall:,.0f} / month required to meet target.")