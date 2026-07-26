import streamlit as st
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_setting, set_setting

st.set_page_config(page_title="Settings | Financial Voice", layout="wide")
init_db()

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
        <div class="header-title">System Settings & Data Management</div>
        <div class="header-sub">Security Passcode Controls, Database Backup & Local Storage Integrations</div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        st.subheader("Security & Passcode Control")
        current_pin = get_setting('user_pin', '1234')
        
        new_pin = st.text_input("Set / Update Security PIN (4 Digits):", value=current_pin, type="password", max_chars=4)
        
        if st.button("Save Security PIN", use_container_width=True):
            if len(new_pin) == 4 and new_pin.isdigit():
                set_setting('user_pin', new_pin)
                st.success("Security PIN updated successfully!")
            else:
                st.error("PIN must be exactly 4 numeric digits.")

with col2:
    with st.container(border=True):
        st.subheader("Database Backup & Export")
        st.caption("Download a direct local backup copy of your central SQLite database (`finance.db`):")
        
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/finance.db'))
        
        if os.path.exists(db_path):
            with open(db_path, "rb") as f:
                db_bytes = f.read()
                
            st.download_button(
                label="Download SQLite Database Backup (.db)",
                data=db_bytes,
                file_name="finance_backup.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
        else:
            st.info("Database file initialized in memory.")