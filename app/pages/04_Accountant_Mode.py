import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys, os, importlib
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Accountant Mode | Financial Voice", layout="wide")
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
        <div class="header-title">Accountant Mode — Financial Ratios & Performance Ledger</div>
        <div class="header-sub">Income Statement (P&L), Cash Flow Analysis & Period Filtering</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    df["Date_dt"] = pd.to_datetime(df["Date"])
    
    # 🗓️ PERIOD FILTERING SYSTEM
    st.subheader("Financial Reporting Period Filter")
    p_col1, p_col2 = st.columns([1, 2])
    
    with p_col1:
        period_option = st.selectbox(
            "Select Time Horizon:", 
            ["This Month", "Last Month", "Year to Date (YTD)", "All Time", "Custom Range"]
        )
    
    today = datetime.now()
    
    if period_option == "This Month":
        start_date = datetime(today.year, today.month, 1)
        end_date = today
    elif period_option == "Last Month":
        first_this_month = datetime(today.year, today.month, 1)
        end_date = first_this_month - timedelta(days=1)
        start_date = datetime(end_date.year, end_date.month, 1)
    elif period_option == "Year to Date (YTD)":
        start_date = datetime(today.year, 1, 1)
        end_date = today
    elif period_option == "Custom Range":
        with p_col2:
            c_start, c_end = st.columns(2)
            start_date = c_start.date_input("Start Date", today - timedelta(days=30))
            end_date = c_end.date_input("End Date", today)
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
    else: # All Time
        start_date = df["Date_dt"].min()
        end_date = df["Date_dt"].max()

    # Filtered Dataframe
    filtered_df = df[(df["Date_dt"] >= pd.to_datetime(start_date)) & (df["Date_dt"] <= pd.to_datetime(end_date))]
    
    # Financial Ratios & Metrics
    inc_df = filtered_df[filtered_df["Type"] == "Income"]
    exp_df = filtered_df[filtered_df["Type"] == "Expense"]
    
    total_inc = inc_df["Amount"].sum()
    total_exp = exp_df["Amount"].sum()
    net_profit = total_inc - total_exp
    
    exp_to_income_ratio = (total_exp / total_inc * 100) if total_inc > 0 else 0.0
    profit_margin = (net_profit / total_inc * 100) if total_inc > 0 else 0.0
    
    days_in_period = max(1, (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1)
    daily_burn_rate = total_exp / days_in_period
    
    st.markdown("---")
    st.subheader("Key Financial Diagnostics & Ratios")
    
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Operating Revenue", f"Rs. {total_inc:,.0f}")
    r2.metric("Total Expenditures", f"Rs. {total_exp:,.0f}")
    r3.metric("Expense-to-Income Ratio", f"{exp_to_income_ratio:.1f}%")
    r4.metric("Daily Outflow Burn Rate", f"Rs. {daily_burn_rate:,.0f} / day")
    
    r5, r6, r7, r8 = st.columns(4)
    r5.metric("Net Surplus / Profit", f"Rs. {net_profit:,.0f}")
    r6.metric("Net Profit Margin", f"{profit_margin:.1f}%")
    r7.metric("Reporting Days", f"{days_in_period} Days")
    r8.metric("Audited Transactions", f"{len(filtered_df)}")
    
    st.markdown("---")
    
    tab_pnl, tab_breakdown, tab_raw = st.tabs(["Profit & Loss Statement", "Category Breakdown", "Audited Ledger Table"])
    
    with tab_pnl:
        st.markdown("#### **Profit & Loss (P&L) Statement**")
        pnl_data = {
            "Account Description": [
                "Gross Operating Revenue",
                "Less: Operating Expenditures",
                "Net Operating Profit / (Loss)"
            ],
            "Amount (PKR)": [
                f"Rs. {total_inc:,.2f}",
                f"Rs. ({total_exp:,.2f})",
                f"Rs. {net_profit:,.2f}"
            ],
            "Percentage (%)": [
                "100.0%",
                f"{exp_to_income_ratio:.1f}%",
                f"{profit_margin:.1f}%"
            ]
        }
        st.table(pd.DataFrame(pnl_data))
        
    with tab_breakdown:
        st.markdown("#### **Expenditure Breakdown by Category**")
        if not exp_df.empty:
            cat_summary = exp_df.groupby("Category")["Amount"].agg(["sum", "count"]).reset_index()
            cat_summary.columns = ["Category", "Total Spent (PKR)", "Transaction Count"]
            cat_summary["% Share of Outflow"] = (cat_summary["Total Spent (PKR)"] / total_exp * 100).round(1)
            cat_summary = cat_summary.sort_values(by="Total Spent (PKR)", ascending=False)
            
            st.dataframe(cat_summary, use_container_width=True)
        else:
            st.info("No expense entries found for selected time period.")
            
    with tab_raw:
        st.dataframe(filtered_df[["ID", "Date", "Type", "Category", "Amount", "Description", "Tags"]], use_container_width=True)

else:
    st.info("Database empty. Add transactions to compute financial accounting reports.")