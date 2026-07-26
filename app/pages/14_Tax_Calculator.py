import streamlit as st
import pandas as pd
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Pakistan Tax Calculator | Financial Voice", layout="wide")
init_db()

# Security Check
saved_pin = get_setting('user_pin', None)
if saved_pin and not st.session_state.get('authenticated', False):
    st.warning("Security PIN required. Please authenticate from the main page.")
    st.stop()

# Corporate Clean Header
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
        <div class="header-title">Pakistan Income Tax Computation Tool (FBR Compliant)</div>
        <div class="header-sub">Annual Tax Liability Estimation for Salaried & Business / Freelancer Individuals</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()
db_annual_income = 0.0

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    total_inc = df[df["Type"] == "Income"]["Amount"].sum()
    # Annualized assumption (if database has monthly records)
    db_annual_income = total_inc * 12.0 if total_inc < 300000 else total_inc

col_in, col_out = st.columns([1, 1])

with col_in:
    with st.container(border=True):
        st.subheader("Taxpayer Configuration")
        taxpayer_type = st.radio("Taxpayer Category", ["Salaried Individual", "Business / Freelancer / Non-Salaried"])
        
        annual_gross = st.number_input(
            "Estimated Annual Gross Income (Rs.)", 
            value=float(db_annual_income) if db_annual_income > 0 else 1200000.0, 
            step=50000.0
        )
        deductible_expenses = st.number_input("Tax-Deductible Allowances / Expenses (Rs.)", value=0.0, step=10000.0)

taxable_income = max(0.0, annual_gross - deductible_expenses)

# FBR Tax Computation Logic
def calculate_pkr_tax(income, is_salaried):
    tax = 0.0
    if is_salaried:
        # Salaried Slabs
        if income <= 600000:
            tax = 0.0
        elif income <= 1200000:
            tax = (income - 600000) * 0.05
        elif income <= 2200000:
            tax = 30000 + (income - 1200000) * 0.15
        elif income <= 3200000:
            tax = 180000 + (income - 2200000) * 0.25
        elif income <= 4100000:
            tax = 430000 + (income - 3200000) * 0.30
        else:
            tax = 700000 + (income - 4100000) * 0.35
    else:
        # Non-Salaried / Business Slabs
        if income <= 600000:
            tax = 0.0
        elif income <= 1200000:
            tax = (income - 600000) * 0.15
        elif income <= 1600000:
            tax = 90000 + (income - 1200000) * 0.20
        elif income <= 3200000:
            tax = 170000 + (income - 1600000) * 0.30
        elif income <= 5600000:
            tax = 650000 + (income - 3200000) * 0.40
        else:
            tax = 1610000 + (income - 5600000) * 0.45
            
    return tax

annual_tax = calculate_pkr_tax(taxable_income, is_salaried=(taxpayer_type == "Salaried Individual"))
monthly_tax = annual_tax / 12.0
effective_tax_rate = (annual_tax / annual_gross * 100) if annual_gross > 0 else 0.0

with col_out:
    with st.container(border=True):
        st.subheader("Tax Liability Summary")
        st.write(f"• **Taxpayer Type:** {taxpayer_type}")
        st.write(f"• **Gross Annual Revenue:** Rs. {annual_gross:,.2f}")
        st.write(f"• **Net Taxable Income:** Rs. {taxable_income:,.2f}")
        
        st.markdown("---")
        st.markdown("#### **Tax Payable Computation:**")
        st.metric("Total Annual Tax Liability", f"Rs. {annual_tax:,.0f}")
        st.metric("Estimated Monthly Tax Deduction", f"Rs. {monthly_tax:,.0f}")
        st.caption(f"Effective Tax Rate: **{effective_tax_rate:.2f}%**")
        
        st.markdown("---")
        st.info("Computed as per statutory FBR tax slabs for Pakistan. Consult a chartered accountant for official tax filing.")