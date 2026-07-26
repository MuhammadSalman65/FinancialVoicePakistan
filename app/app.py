import streamlit as st

# Step 1: Agar user ne abhi tak passcode set nahi kiya (Pehli dafa aaya hai)
if "user_passcode" not in st.session_state:
    st.title("🔒 Welcome to Financial Voice Pakistan")
    st.subheader("Set Your Personal Passcode")
    st.info("Apni marzi ka 4-digit ya koi bhi Passcode set karein taake aap ki session security active ho jaye.")
    
    new_pin = st.text_input("Create Your Passcode:", type="password", key="setup_pin")
    
    if st.button("Set Passcode & Enter", use_container_width=True):
        if new_pin.strip():
            st.session_state["user_passcode"] = new_pin
            st.session_state["authenticated"] = True
            st.success("Passcode Set Successfully!")
            st.rerun()
        else:
            st.warning("Please enter a valid passcode!")
    st.stop()

# Step 2: Agar user logout ho jaye toh wahi passcode maange
if not st.session_state.get("authenticated", False):
    st.title("🔑 Passcode Verification")
    entered_pin = st.text_input("Enter Your Passcode:", type="password", key="login_pin")
    
    if st.button("Unlock Application", use_container_width=True):
        if entered_pin == st.session_state["user_passcode"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect passcode! Please try again.")
    st.stop()