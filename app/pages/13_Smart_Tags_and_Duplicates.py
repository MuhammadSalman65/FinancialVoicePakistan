import streamlit as st
import pandas as pd
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_all_transactions, delete_transaction, get_setting

st.set_page_config(page_title="Tags & Duplicate Audit | Financial Voice", layout="wide")
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
        <div class="header-title">Data Quality Engine — Tagging & Duplicate Audit</div>
        <div class="header-sub">Automated Duplicate Transaction Detection & Analytical Hashtag Filtering</div>
    </div>
""", unsafe_allow_html=True)

rows = get_all_transactions()

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Date", "Amount", "Category", "Description", "Type", 
        "Timestamp", "Confidence", "Edited", "Tags", "Recurring"
    ])
    
    tab_dup, tab_tags = st.tabs(["Duplicate Transaction Detector", "Hashtag & Tag Analytics"])
    
    with tab_dup:
        st.subheader("Potential Duplicate Audit")
        st.caption("Transactions sharing the exact same Date, Amount, and Category are flagged below:")
        
        # Group by Date, Amount, Category to find duplicates
        dup_mask = df.duplicated(subset=["Date", "Amount", "Category"], keep=False)
        duplicates_df = df[dup_mask].sort_values(by=["Date", "Amount"])
        
        if not duplicates_df.empty:
            st.error(f"Attention: {len(duplicates_df)} potential duplicate entries detected.")
            st.dataframe(duplicates_df[["ID", "Date", "Type", "Category", "Amount", "Description", "Timestamp"]], use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### **Duplicate Resolution Action**")
            dup_id_to_del = st.number_input("Enter ID of Duplicate Entry to Remove:", min_value=1, step=1)
            if st.button("Delete Selected Duplicate Record", use_container_width=True):
                delete_transaction(int(dup_id_to_del))
                st.success(f"Record ID {dup_id_to_del} removed permanently.")
                st.rerun()
        else:
            st.success("Clean Ledger: No duplicate entries found in current database.")

    with tab_tags:
        st.subheader("Hashtag & Keyword Analysis")
        tag_search = st.text_input("Filter Ledger by Tag or Keyword (e.g., #committee, #udhaar, fuel):")
        
        if tag_search:
            filtered_tags_df = df[
                df["Description"].str.contains(tag_search, case=False, na=False) | 
                df["Tags"].str.contains(tag_search, case=False, na=False)
            ]
            st.write(f"Found **{len(filtered_tags_df)}** matching records:")
            st.dataframe(filtered_tags_df[["ID", "Date", "Type", "Category", "Amount", "Description", "Tags"]], use_container_width=True)
            
            tot_matched = filtered_tags_df["Amount"].sum()
            st.info(f"Total Combined Value for '{tag_search}': **Rs. {tot_matched:,.2f}**")
        else:
            st.info("Enter a tag or keyword above to isolate specific expenditure themes.")

else:
    st.info("No records in database to analyze for duplicates or tags.")