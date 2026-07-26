import streamlit as st
import pandas as pd
import sys, os, importlib
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Executive Report Export | Financial Voice", layout="wide")
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
    .report-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 30px;
        border-radius: 12px;
        color: #0f172a;
        font-family: Arial, sans-serif;
    }
    </style>
    <div class="header-banner">
        <div class="header-title">Formal Financial Report Generator</div>
        <div class="header-sub">Audit-Grade Executive Statement & PDF / HTML Document Export</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    net_surplus = total_income - total_expense
    margin = (net_surplus / total_income * 100) if total_income > 0 else 0.0
    
    cat_summary = df[df["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
    
    st.subheader("Report Configuration & Filter")
    c1, c2 = st.columns(2)
    company_title = c1.text_input("Entity / Individual Name", value="Muhammad Salman — Financial Ledger")
    report_period = c2.text_input("Reporting Period", value=datetime.now().strftime("%B %Y"))
    
    st.markdown("---")
    st.subheader("Document Live Preview")
    
    # HTML Report Generator
    html_report = f"""
    <div class="report-card">
        <div style="text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #0f172a;">{company_title}</h2>
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 14px;">FINANCIAL PERFORMANCE REPORT | PERIOD: {report_period}</p>
        </div>
        
        <h4 style="color: #0284c7; margin-bottom: 10px;">1. EXECUTIVE FINANCIAL SUMMARY</h4>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
            <tr style="background: #f1f5f9;">
                <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Gross Operating Revenue</b></td>
                <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;"><b>PKR {total_income:,.2f}</b></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Total Operating Expenditures</b></td>
                <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; color: #dc2626;"><b>PKR {total_expense:,.2f}</b></td>
            </tr>
            <tr style="background: #f1f5f9;">
                <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Net Profit / Surplus</b></td>
                <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; color: #16a34a;"><b>PKR {net_surplus:,.2f}</b></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #cbd5e1;"><b>Net Profit Margin (%)</b></td>
                <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;"><b>{margin:.2f}%</b></td>
            </tr>
        </table>
        
        <h4 style="color: #0284c7; margin-bottom: 10px;">2. OPERATING EXPENDITURE BREAKDOWN</h4>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
            <thead>
                <tr style="background: #0f172a; color: white;">
                    <th style="padding: 8px; text-align: left;">Category</th>
                    <th style="padding: 8px; text-align: right;">Amount (PKR)</th>
                    <th style="padding: 8px; text-align: right;">% of Total Outflow</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in cat_summary.iterrows():
        cat_pct = (row["Amount"] / total_expense * 100) if total_expense > 0 else 0.0
        html_report += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #cbd5e1;">{row['Category']}</td>
                <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right;">{row['Amount']:,.2f}</td>
                <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right;">{cat_pct:.1f}%</td>
            </tr>
        """
        
    html_report += f"""
            </tbody>
        </table>
        
        <div style="margin-top: 30px; font-size: 11px; color: #94a3b8; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 10px;">
            Generated by Financial Voice Pakistan — Executive FinTech Suite | Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    """
    
    st.markdown(html_report, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Download Options")
    
    d1, d2 = st.columns(2)
    d1.download_button(
        label="Download Formal Report (HTML File)",
        data=html_report,
        file_name=f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True
    )
    
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    d2.download_button(
        label="Download Raw Data Ledger (CSV)",
        data=csv_bytes,
        file_name=f"Ledger_Export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("No database records available to construct formal financial statement.")