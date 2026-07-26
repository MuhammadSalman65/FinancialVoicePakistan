import streamlit as st
import sys, os, importlib
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
import src.parser as parser

importlib.reload(db)
importlib.reload(parser)

from src.database import init_db, add_transaction, get_setting
from src.parser import parse_transaction

st.set_page_config(page_title="Voice Entry | Financial Voice", layout="wide")
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
        <div class="header-title">Voice & NLP Transaction Logger</div>
        <div class="header-sub">Hybrid Machine Learning & Rule-Based Intent Extraction</div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        st.subheader("Transaction Speech / Text Input")
        st.caption("Enter or dictate transaction details in plain English or Urdu:")
        
        user_input = st.text_area(
            "Speech Transcript / Raw Text:",
            value="PPSO pump se bike full karwai 1800 rupees mein",
            height=120
        )
        
        parse_btn = st.button("Parse Transaction with AI/ML Engine", use_container_width=True)

if parse_btn or user_input:
    parsed_data = parse_transaction(user_input)
    
    with col2:
        with st.container(border=True):
            st.subheader("Extracted Transaction Preview")
            
            p_date = st.date_input("Date", datetime.now())
            p_type = st.radio("Type", ["Expense", "Income"], index=0 if parsed_data["type"] == "Expense" else 1, horizontal=True)
            p_amount = st.number_input("Amount (PKR)", value=float(parsed_data["amount"]), step=500.0)
            
            categories = ["Groceries", "Utilities", "Transportation", "Dining", "Health", "Housing", "Salary", "Committee/Savings", "Udhaar/Credit", "Other"]
            cat_idx = categories.index(parsed_data["category"]) if parsed_data["category"] in categories else len(categories)-1
            p_category = st.selectbox("Category", categories, index=cat_idx)
            
            p_desc = st.text_input("Description", value=parsed_data["description"])
            p_tags = st.text_input("Auto-Generated Hashtags", value=parsed_data["tags"])
            
            st.info(f"Classification Engine: **{parsed_data['engine']}**")
            
            if st.button("Confirm & Post to Central Database", use_container_width=True):
                add_transaction(
                    date=p_date.strftime("%Y-%m-%d"),
                    amount=p_amount,
                    category=p_category,
                    description=p_desc,
                    trans_type=p_type,
                    tags=p_tags
                )
                st.success("Successfully posted transaction to Central Ledger!")