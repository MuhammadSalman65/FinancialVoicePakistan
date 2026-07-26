import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, get_setting

st.set_page_config(page_title="Household Mode | Financial Voice", layout="wide")
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
        <div class="header-title">Household & Family Financial Analytics</div>
        <div class="header-sub">Multi-Member Expense Allocation, Joint Budgeting & Contribution Breakdown</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()
if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    
    # Extract or infer family member attribution from tags/description
    def detect_member(row):
        desc = str(row["Description"]).lower()
        tag = str(row["Tags"]).lower()
        text = f"{desc} {tag}"
        
        if any(w in text for w in ["abbu", "father", "head", "rent", "utilities"]):
            return "Household Head (Abbu/Father)"
        elif any(w in text for w in ["amma", "mother", "groceries", "kitchen", "ration"]):
            return "Domestic / Kitchen (Amma)"
        elif any(w in text for w in ["bhai", "brother", "sister"]):
            return "Siblings"
        else:
            return "Personal (Self)"

    df["Member"] = df.apply(detect_member, axis=1)
    
    exp_df = df[df["Type"] == "Expense"]
    total_hh_expense = exp_df["Amount"].sum() if not exp_df.empty else 0.0
    
    st.subheader("Household Summary Metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Household Outflow", f"Rs. {total_hh_expense:,.0f}")
    
    member_spending = exp_df.groupby("Member")["Amount"].sum() if not exp_df.empty else pd.Series()
    top_contributor = member_spending.idxmax() if not member_spending.empty else "N/A"
    top_amount = member_spending.max() if not member_spending.empty else 0.0
    
    m2.metric("Primary Outflow Category", top_contributor)
    m3.metric("Primary Category Amount", f"Rs. {top_amount:,.0f}")
    
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Expense Distribution by Family Role")
        if not exp_df.empty:
            fig_pie = px.pie(
                exp_df, 
                values='Amount', 
                names='Member', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pie.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No household expense records available.")

    with col_chart2:
        st.subheader("Member vs Category Matrix")
        if not exp_df.empty:
            pivot_df = exp_df.groupby(["Member", "Category"])["Amount"].sum().reset_index()
            fig_bar = px.bar(
                pivot_df, 
                x="Member", 
                y="Amount", 
                color="Category", 
                text_auto=',.0f'
            )
            fig_bar.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available.")

    st.markdown("---")
    st.subheader("Member-Wise Detailed Ledger Breakdown")
    selected_member = st.selectbox("Filter Ledger by Member Role:", ["All Members"] + list(df["Member"].unique()))
    
    if selected_member != "All Members":
        filtered_member_df = df[df["Member"] == selected_member]
    else:
        filtered_member_df = df
        
    st.dataframe(filtered_member_df[["ID", "Date", "Member", "Type", "Category", "Amount", "Description"]], use_container_width=True)

else:
    st.info("No records found in database. Add transactions to generate household analytics.")