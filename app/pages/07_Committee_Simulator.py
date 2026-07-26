import streamlit as st
import pandas as pd
import sys, os, importlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, add_transaction, get_setting

st.set_page_config(page_title="Committee Simulator | Financial Voice", layout="wide")
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
        <div class="header-title">ROSCA / Committee Financial Simulator & Ledger Integration</div>
        <div class="header-sub">Local Savings Mechanism, Opportunity Cost & Central Database Synchronization</div>
    </div>
""", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1])

with col_input:
    with st.container(border=True):
        st.subheader("Committee Details Configuration")
        c_name = st.text_input("Committee / Club Name", value="Mohalla Saving Club")
        monthly_amount = st.number_input("Monthly Contribution (Rs.)", value=25000.0, step=5000.0)
        total_members = st.number_input("Total Members / Months", value=10, min_value=2, max_value=60)
        user_turn = st.number_input("Your Turn Position (1st, 2nd, etc.)", value=7, min_value=1, max_value=int(total_members))
        expected_rate = st.slider("Benchmark Investment Rate (% Annual Return)", min_value=3.0, max_value=15.0, value=8.0)

total_pool = monthly_amount * total_members
months_to_wait = user_turn - 1
payout_date = datetime.now() + relativedelta(months=months_to_wait)

# Opportunity Cost Calculation
monthly_rate = (expected_rate / 100) / 12
fv_investment = 0.0
for m in range(int(total_members)):
    fv_investment = (fv_investment + monthly_amount) * (1 + monthly_rate)

opp_cost_diff = fv_investment - total_pool

with col_output:
    with st.container(border=True):
        st.subheader("Simulation Results & Analysis")
        st.write(f"• **Committee Name:** {c_name}")
        st.write(f"• **Total Payout Amount:** Rs. {total_pool:,.0f}")
        st.write(f"• **Expected Payout Date:** {payout_date.strftime('%B %Y')} ({months_to_wait} months wait)")
        
        st.markdown("---")
        st.markdown("#### **Financial Position Analysis:**")
        
        if user_turn <= (total_members / 2):
            st.info(f"Position Type: Early Receiver (Turn #{user_turn}). Functionally acts as an **Interest-Free Loan** of Rs. {total_pool:,.0f} received upfront.")
        else:
            st.warning(f"Position Type: Late Receiver (Turn #{user_turn}). Functionally acts as a **Forced Saving Mechanism** with waiting period.")

        st.markdown("---")
        st.markdown("#### **Opportunity Cost Assessment:**")
        st.write(f"• Equivalent Bank / NSC Value (@ {expected_rate:.1f}% Return): **Rs. {fv_investment:,.0f}**")
        
        if opp_cost_diff > 0:
            st.caption(f"Opportunity Cost Variance: Investing the same monthly amount in a benchmark vehicle yields ~Rs. {opp_cost_diff:,.0f} additional return over {total_members} months.")

        # DIRECT INTEGRATION WITH CENTRAL DATABASE
        st.markdown("---")
        st.markdown("#### **Central Database Ledger Integration**")
        st.caption("Post this committee transaction directly to your main ledger:")
        
        c_btn1, c_btn2 = st.columns(2)
        
        if c_btn1.button("Post Monthly Installment (Expense)", use_container_width=True):
            add_transaction(
                date=datetime.now().strftime("%Y-%m-%d"),
                amount=monthly_amount,
                category="Committee/Savings",
                description=f"Monthly Committee Installment: {c_name}",
                trans_type="Expense",
                tags="#committee #savings"
            )
            st.success("Successfully posted Rs. {:,.0f} Committee Expense to Central Ledger!".format(monthly_amount))

        if c_btn2.button("Post Full Payout (Income)", use_container_width=True):
            add_transaction(
                date=payout_date.strftime("%Y-%m-%d"),
                amount=total_pool,
                category="Committee/Savings",
                description=f"Committee Lump Sum Payout: {c_name} (Turn #{user_turn})",
                trans_type="Income",
                tags="#committee #payout"
            )
            st.success("Successfully posted Rs. {:,.0f} Committee Income Payout to Central Ledger!".format(total_pool))