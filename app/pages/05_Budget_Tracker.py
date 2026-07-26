import streamlit as st
import pandas as pd
import sys, os, importlib
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Budget Tracker | Financial Voice", layout="wide")
init_db()

# Security Check
saved_pin = get_setting('user_pin', None)
if saved_pin and not st.session_state.get('authenticated', False):
    st.warning("Security PIN required. Please authenticate from the main page.")
    st.stop()

# Header Banner
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
        <div class="header-title">Monthly Budget Controls & Variance Alerts</div>
        <div class="header-sub">Category Threshold Monitoring, Utilization Ratios & Over-Budget Prevention</div>
    </div>
""", unsafe_allow_html=True)

# Default Monthly Budget Targets (PKR)
DEFAULT_BUDGETS = {
    "Groceries": 45000.0,
    "Utilities": 25000.0,
    "Transportation": 20000.0,
    "Dining": 15000.0,
    "Health": 10000.0,
    "Housing": 35000.0,
    "Other": 15000.0
}

rows = get_all_transactions()
today = datetime.now()
current_month_str = today.strftime("%B %Y")

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    df["Date_dt"] = pd.to_datetime(df["Date"])
    
    # Filter Current Month Expenses Only
    month_mask = (df["Date_dt"].dt.year == today.year) & (df["Date_dt"].dt.month == today.month)
    month_exp_df = df[month_mask & (df["Type"] == "Expense")]
    
    cat_actuals = month_exp_df.groupby("Category")["Amount"].sum().to_dict()
else:
    cat_actuals = {}

st.subheader(f"Budget Configuration & Live Consumption ({current_month_str})")

col_config, col_status = st.columns([1, 1.5])

with col_config:
    with st.container(border=True):
        st.markdown("#### **Monthly Category Limits (PKR)**")
        user_budgets = {}
        for cat, default_val in DEFAULT_BUDGETS.items():
            user_budgets[cat] = st.number_input(
                f"{cat} Limit:", 
                value=float(default_val), 
                step=2500.0, 
                key=f"b_{cat}"
            )

total_budget = sum(user_budgets.values())
total_actual = sum(cat_actuals.values())
overall_utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0.0

with col_status:
    with st.container(border=True):
        st.markdown("#### **Overall Monthly Budget Summary**")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Monthly Limit", f"Rs. {total_budget:,.0f}")
        m2.metric("Total Spent So Far", f"Rs. {total_actual:,.0f}")
        m3.metric("Overall Utilization", f"{overall_utilization:.1f}%")
        
        if overall_utilization >= 100.0:
            st.error("Critical Alert: Total monthly expenditure has exceeded the defined budget ceiling!")
        elif overall_utilization >= 80.0:
            st.warning("Warning: Total monthly expenditure is approaching the budget limit.")
        else:
            st.success("Healthy Spending: Overall expenditure is well within monthly limits.")

    st.markdown("---")
    st.markdown("#### **Category Breakdown & Utilization Progress**")
    
    for cat, limit in user_budgets.items():
        actual = cat_actuals.get(cat, 0.0)
        pct = min(100.0, (actual / limit * 100)) if limit > 0 else 0.0
        remaining = limit - actual
        
        st.write(f"**{cat}** — Spent: **Rs. {actual:,.0f}** / Limit: **Rs. {limit:,.0f}**")
        
        if actual > limit:
            st.progress(1.0)
            st.caption(f"Over budget by **Rs. {abs(remaining):,.0f}** ({pct:.1f}% used)")
        else:
            st.progress(pct / 100.0)
            st.caption(f"Remaining: **Rs. {remaining:,.0f}** ({pct:.1f}% used)")
        st.write("")