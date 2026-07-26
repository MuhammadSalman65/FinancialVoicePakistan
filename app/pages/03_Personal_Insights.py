import streamlit as st
import pandas as pd
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
import src.analytics as analytics

importlib.reload(db)
importlib.reload(analytics)

from src.database import init_db, get_all_transactions, get_setting
from src.analytics import calculate_health_score

st.set_page_config(page_title="Personal Insights | Financial Voice", layout="wide")
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
        <div class="header-title">AI Personal Insights & Financial Runway Diagnostics</div>
        <div class="header-sub">Emergency Fund Preparedness, Spending Ratios & Actionable Recommendations</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    df["Date_dt"] = pd.to_datetime(df["Date"])
    
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    net_savings = max(0.0, total_income - total_expense)
    
    # Calculate Monthly Average Outflow
    unique_months = max(1, df["Date_dt"].dt.to_period("M").nunique())
    avg_monthly_expense = total_expense / unique_months
    
    # Financial Runway (Emergency Fund Coverage in Months)
    runway_months = (net_savings / avg_monthly_expense) if avg_monthly_expense > 0 else 0.0
    
    score, health_summary = calculate_health_score(df)
    
    st.subheader("Financial Liquidity & Emergency Preparedness")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Net Capital", f"Rs. {net_savings:,.0f}")
    m2.metric("Avg Monthly Outflow", f"Rs. {avg_monthly_expense:,.0f}")
    m3.metric("Emergency Runway", f"{runway_months:.1f} Months")
    m4.metric("AI Health Score", f"{score} / 100")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        with st.container(border=True):
            st.markdown("#### **Emergency Fund Runway Analysis**")
            if runway_months >= 6.0:
                st.success("Strong Reserve: You have over 6 months of emergency runway saved. Highly resilient position.")
            elif runway_months >= 3.0:
                st.warning("Moderate Reserve: You have 3 to 6 months of runway. Consider increasing liquid savings.")
            else:
                st.error("Low Reserve: Emergency runway is below 3 months. High vulnerability to unexpected income shocks.")
                
            st.markdown("---")
            st.markdown("#### **50 / 30 / 20 Budget Rule Benchmark**")
            
            needs = total_expense * 0.60  # Estimated Essentials
            wants = total_expense * 0.40  # Estimated Discretionary
            
            st.write(f"• **Essential Expenses (Needs):** ~Rs. {needs:,.0f}")
            st.write(f"• **Discretionary Expenses (Wants):** ~Rs. {wants:,.0f}")
            st.write(f"• **Net Savings Capacity:** Rs. {net_savings:,.0f}")

    with col_right:
        with st.container(border=True):
            st.markdown("#### **Strategic AI Financial Recommendations**")
            st.markdown(health_summary)

else:
    st.info("No records in database to perform runway diagnostics. Add transactions to begin.")