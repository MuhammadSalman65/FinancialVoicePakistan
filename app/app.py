import streamlit as st
import sys, os, importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.database as db
importlib.reload(db)

from src.database import init_db, get_setting, set_setting

st.set_page_config(
    page_title="Financial Voice Pakistan",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

saved_pin = get_setting('user_pin', None)

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc !important; }
    .header-banner {
        background: #0f172a; padding: 24px 30px; border-radius: 12px;
        color: #ffffff; border-bottom: 3px solid #0284c7; margin-bottom: 24px;
    }
    .header-title { font-size: 24px; font-weight: 700; color: #f8fafc; margin: 0; }
    .header-sub { color: #38bdf8; font-size: 13px; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# AUTHENTICATION CHECK
if not st.session_state['authenticated']:
    st.markdown("""
        <div class="header-banner">
            <div class="header-title">Financial Voice Pakistan</div>
            <div class="header-sub">Enterprise Security Architecture & Access Control</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            if saved_pin is None:
                st.subheader("Set Initial Security PIN")
                p1 = st.text_input("New PIN Code", type="password")
                p2 = st.text_input("Confirm PIN Code", type="password")
                if st.button("Initialize & Unlock System", use_container_width=True):
                    if len(p1) >= 4 and p1 == p2:
                        set_setting('user_pin', p1)
                        st.session_state['authenticated'] = True
                        st.success("Passcode saved. Redirecting...")
                        st.rerun()
                    else:
                        st.error("PINs do not match or are shorter than 4 digits.")
            else:
                st.subheader("Passcode Verification")
                entered_pin = st.text_input("Enter Passcode", type="password")
                if st.button("Unlock Application", use_container_width=True):
                    if entered_pin == saved_pin:
                        st.session_state['authenticated'] = True
                        st.success("Access Granted. Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid Security Passcode.")
    st.stop()

# REDIRECT TO DASHBOARD
st.switch_page("pages/01_Home_Dashboard.py")