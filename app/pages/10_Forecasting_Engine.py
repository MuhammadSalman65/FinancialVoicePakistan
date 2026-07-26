import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os, importlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Forecasting Engine | Financial Voice", layout="wide")
init_db()

# Security Check
saved_pin = get_setting('user_pin', None)
if saved_pin and not st.session_state.get('authenticated', False):
    st.warning("Security PIN required. Please authenticate from the main page.")
    st.stop()

# Clean Corporate English Header
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
        <div class="header-title">Predictive Financial Forecasting Engine</div>
        <div class="header-sub">Statistical Trend Extrapolation & Forward Expenditure Modeling</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    
    df["Date_dt"] = pd.to_datetime(df["Date"])
    df["Month_Year"] = df["Date_dt"].dt.strftime("%Y-%m")
    
    exp_df = df[df["Type"] == "Expense"].copy()
    
    if not exp_df.empty:
        monthly_exp = exp_df.groupby("Month_Year")["Amount"].sum().reset_index()
        monthly_exp = monthly_exp.sort_values("Month_Year")
        
        # Calculate Forecasting Metrics
        hist_count = len(monthly_exp)
        latest_actual = monthly_exp["Amount"].iloc[-1]
        
        if hist_count >= 2:
            # Weighted Moving Average + Trend Factor
            weights = np.arange(1, hist_count + 1)
            wma = np.average(monthly_exp["Amount"], weights=weights)
            growth_rate = (monthly_exp["Amount"].pct_change().dropna().mean()) if hist_count > 2 else 0.05
            
            forecast_next_month = max(0.0, wma * (1.0 + max(-0.2, min(0.3, growth_rate))))
            confidence_bound = forecast_next_month * 0.08
        else:
            wma = latest_actual
            forecast_next_month = latest_actual * 1.05
            confidence_bound = forecast_next_month * 0.10

        # Calculate Next Month Name
        last_month_dt = datetime.strptime(monthly_exp["Month_Year"].iloc[-1], "%Y-%m")
        next_month_dt = last_month_dt + relativedelta(months=1)
        next_month_str = next_month_dt.strftime("%B %Y")
        
        # Display Key Forecast Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Historical Monthly Average", f"Rs. {monthly_exp['Amount'].mean():,.0f}")
        m2.metric(f"Forecasted Outflow ({next_month_str})", f"Rs. {forecast_next_month:,.0f}", delta=f"± Rs. {confidence_bound:,.0f} Variance")
        m3.metric("Latest Month Expense", f"Rs. {latest_actual:,.0f}")
        
        st.markdown("---")
        
        col_plot, col_cat = st.columns([1.5, 1])
        
        with col_plot:
            st.subheader("Historical vs Projected Outflow Trend")
            
            # Combine Historical + Forecast dataframe for chart
            plot_df = monthly_exp.copy()
            plot_df["Status"] = "Historical"
            
            forecast_row = pd.DataFrame([{
                "Month_Year": next_month_dt.strftime("%Y-%m"),
                "Amount": forecast_next_month,
                "Status": "Forecasted"
            }])
            
            chart_df = pd.concat([plot_df, forecast_row], ignore_index=True)
            
            fig_trend = px.line(
                chart_df, 
                x="Month_Year", 
                y="Amount", 
                color="Status", 
                markers=True,
                color_discrete_map={"Historical": "#0284c7", "Forecasted": "#ef4444"}
            )
            fig_trend.update_layout(height=360, hovermode="x unified", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_cat:
            st.subheader("Category-Wise Projections")
            cat_exp = exp_df.groupby("Category")["Amount"].sum().reset_index()
            total_cat_sum = cat_exp["Amount"].sum()
            
            if total_cat_sum > 0:
                cat_exp["Proportion"] = cat_exp["Amount"] / total_cat_sum
                cat_exp["Projected_Amount"] = cat_exp["Proportion"] * forecast_next_month
                cat_exp = cat_exp.sort_values("Projected_Amount", ascending=False)
                
                with st.container(border=True):
                    for _, row in cat_exp.iterrows():
                        st.write(f"• **{row['Category']}:** Rs. {row['Projected_Amount']:,.0f}")
            else:
                st.info("No category data available for forecast breakdown.")

    else:
        st.info("No expense records found. Enter transactions to generate forecast analytics.")
else:
    st.info("Database empty. Add records to enable forecasting engine.")