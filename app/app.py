import streamlit as st

st.set_page_config(page_title="Financial Voice Pakistan", layout="wide")

# 1. Passcode Check & Setup Block
if "user_passcode" not in st.session_state:
    st.title("🔒 Financial Voice Pakistan")
    st.subheader("Set Your Session Passcode")
    st.info("💡 Portfolio Security Demo: Set any passcode below to unlock the dashboard.")
    
    new_pin = st.text_input("Create Your Passcode:", type="password", key="setup_pin")
    if st.button("Unlock Dashboard", use_container_width=True):
        if new_pin.strip():
            st.session_state["user_passcode"] = new_pin
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.warning("Please enter a valid passcode!")
    st.stop()  # Is point par script ruk jaye gi jab tak passcode enter na ho

# 2. Main Application Content (Passcode enter hone ke baad yeh chalega)
st.sidebar.success("🔑 Authenticated Session")
st.title("📊 Financial Voice Pakistan - Central Dashboard")
st.success("🎉 Access Granted! Welcome to the suite.")
st.info("👈 Please select a module from the sidebar on the left to explore.")

# Redirection to main home page if using multi-page structure
try:
    st.switch_page("pages/01_Home_Dashboard.py")
except Exception:
    pass