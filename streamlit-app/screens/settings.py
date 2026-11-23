import streamlit as st

from api.auth import logout
from components.footer import render_footer
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from utils.constants import APP_NAME, LOGIN
from utils.helpers import current_user, go_to, is_authenticated
from utils.session import logout_user


def render() -> None:
    """Render the settings screen."""
    if not is_authenticated():
        st.warning("Please login first.")
        go_to(LOGIN)
        return

    render_sidebar()
    render_navbar()
    st.title("⚙ Settings")
    st.caption("Manage your account and application preferences.")

    user = current_user()
    st.subheader("👤 Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Username", value=user.get("user_name", ""), disabled=True)
    with col2:
        st.text_input("Email", value=user.get("email_id", ""), disabled=True)

    st.divider()
    st.subheader("📈 Chart Preferences")
    periods = ["5d", "1mo", "3mo", "6mo", "1y", "5y", "max"]
    selected_period = st.selectbox(
        "Default Chart Period", periods,
        index=periods.index(st.session_state.get("chart_period", "5d")),
    )
    st.session_state["chart_period"] = selected_period

    st.divider()
    st.subheader("🎨 Appearance")
    theme = st.radio("Theme", ["Dark", "Light"], horizontal=True, index=0)
    st.caption(f"Current theme: {theme}")

    st.divider()
    st.subheader("ℹ About")
    st.write(f"**Application:** {APP_NAME}")
    st.write("**Version:** 1.0.0")
    st.write("**Backend:** FastAPI")
    st.write("**Frontend:** Streamlit")
    st.write("**Data Source:** Yahoo Finance")

    st.divider()
    st.subheader("🔒 Session")
    if st.button("Logout", type="primary", width="stretch"):
        result = logout()
        logout_user()
        if result.get("status") == "success":
            st.success("You have been logged out.")
        else:
            st.warning(
                "This device is logged out, but the server could not confirm token "
                "revocation. The token remains valid only until its configured expiry."
            )
        st.rerun()
    render_footer()
