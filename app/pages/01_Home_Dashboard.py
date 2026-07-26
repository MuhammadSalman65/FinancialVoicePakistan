import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os, importlib
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
import src.analytics as analytics

importlib.reload(db)
importlib.reload(analytics)

from src.database import init_db, get_all_transactions, get_setting
from src.analytics import calculate_health_score

st.set_page_config(page_title="Home Dashboard | Financial Voice", layout="wide")
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
        <div class="header-title">Financial Voice Pakistan — Personal Financial Intelligence</div>
        <div class="header-sub">Real-Time Financial Pulse, Period Analytics & Health Diagnostics</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()
if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    df["Date_dt"] = pd.to_datetime(df["Date"])
    
    # Filter Bar
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        period_filter = st.selectbox("Dashboard View Period:", ["This Month", "Last Month", "YTD", "All Time"])
    
    today = datetime.now()
    if period_filter == "This Month":
        filtered_df = df[df["Date_dt"] >= datetime(today.year, today.month, 1)]
    elif period_filter == "Last Month":
        first_this = datetime(today.year, today.month, 1)
        last_month_end = first_this - timedelta(days=1)
        last_month_start = datetime(last_month_end.year, last_month_end.month, 1)
        filtered_df = df[(df["Date_dt"] >= last_month_start) & (df["Date_dt"] <= last_month_end)]
    elif period_filter == "YTD":
        filtered_df = df[df["Date_dt"] >= datetime(today.year, 1, 1)]
    else:
        filtered_df = df
    
    total_income = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
    total_expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
    
    score, health_summary = calculate_health_score(filtered_df)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("Financial Pulse")
        delta_str = f"{savings_rate:.1f}% Savings Rate"
        if net_savings < 0:
            st.metric("Net Savings", f"Rs. {net_savings:,.0f}", delta=delta_str, delta_color="inverse")
        else:
            st.metric("Net Savings", f"Rs. {net_savings:,.0f}", delta=delta_str)
        st.caption(f"Income: **Rs. {total_income:,.0f}** | Expenses: **Rs. {total_expense:,.0f}**")
        
    with col2:
        st.subheader("AI Health Score")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#0284c7"},
                'steps' : [
                    {'range': [0, 40], 'color': "#ef4444"},
                    {'range': [40, 70], 'color': "#f59e0b"},
                    {'range': [70, 100], 'color': "#10b981"}
                ],
            }
        ))
        fig_gauge.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col3:
        st.subheader("Expense Trend")
        trend_df = filtered_df[filtered_df["Type"] == "Expense"].groupby("Date")["Amount"].sum().reset_index()
        if not trend_df.empty:
            fig_spark = px.line(trend_df, x="Date", y="Amount", markers=True)
            fig_spark.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10), xaxis_visible=False)
            st.plotly_chart(fig_spark, use_container_width=True)
        else:
            st.info("No expense trends recorded in this period.")

    st.markdown("---")
    with st.container(border=True):
        st.markdown("#### **AI Financial Health Analysis**")
        st.markdown(health_summary)

else:
    st.info("Welcome! Database is currently empty. Navigate to 'Voice Entry' from the sidebar to add records.")