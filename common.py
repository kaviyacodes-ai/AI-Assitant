"""Start-up code shared by every page: page title, key check, optional password."""
import hmac
import streamlit as st
import config


def setup(title, icon):
    st.set_page_config(page_title=title, page_icon=icon)

    # Friendly message instead of a crash when keys are missing
    missing = config.missing_keys()
    if missing:
        st.error(f"Missing in your .env file (or Secrets): {', '.join(missing)}")
        st.stop()

    # Optional password (set APP_PASSWORD in .env or in Streamlit Secrets)
    if config.APP_PASSWORD and not st.session_state.get("authed"):
        st.title("🔒 Sign in")
        entered = st.text_input("Password", type="password")
        if entered and hmac.compare_digest(entered.encode(), config.APP_PASSWORD.encode()):
            st.session_state.authed = True
            st.rerun()
        elif entered:
            st.error("Wrong password")
        st.stop()
