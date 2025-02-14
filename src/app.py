"""
Module: app
Purpose: Entry point for the SkillSync AI Streamlit application.

"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import authentication
from resume_analysis import display_resume_dashboard

# Basic configuration for the Streamlit page.
st.set_page_config(page_title="SkillSync AI", layout="wide")
load_dotenv()

# Retrieve and validate the OpenAI API key.
openai_key = os.getenv("API_KEY")
if not openai_key:
    st.error("API Key is missing. Please check your .env configuration.")
    st.stop()
os.environ["API_KEY"] = openai_key

# Initialize session state variables for user authentication.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_details = None
    st.session_state.user_role = None

# Perform user login if not already authenticated.
if not st.session_state.logged_in:
    st.session_state.logged_in, st.session_state.user_details = authentication.login_user()
    if not st.session_state.logged_in:
        st.stop()

# Provide a logout option.
if st.session_state.logged_in and st.button("Logout"):
    authentication.logout_user()

# Render dashboards based on the user's role.
if st.session_state.logged_in:
    if st.session_state.user_role == "user":
        st.markdown("<h1 style='text-align: center;'>SkillSync AI - User Dashboard</h1>", unsafe_allow_html=True)
        st.write(f"Welcome, {st.session_state.user_details['name']} ({st.session_state.user_details['email']})!")
        display_resume_dashboard()
    elif st.session_state.user_role == "admin":
        st.markdown("<h1 style='text-align: center;'>SkillSync AI - Admin Dashboard</h1>", unsafe_allow_html=True)
        st.write(f"Welcome, {st.session_state.user_details['name']} ({st.session_state.user_details['email']})!")
        admin_option = st.sidebar.radio("Administration Options", ["User Analytics", "Resume Evaluation"])
        if admin_option == "User Analytics":
            st.subheader("User & Usage Analytics")
            users = authentication.firestore_db.collection("users").stream()
            users_data = [user.to_dict() for user in users]
            usage = authentication.firestore_db.collection("usage_logs").stream()
            usage_data = [log.to_dict() for log in usage]
            if users_data and usage_data:
                df_users = pd.DataFrame(users_data)
                df_usage = pd.DataFrame(usage_data)
                merged_df = pd.merge(df_users, df_usage, left_on="email", right_on="user_email", how="left")
                merged_df = merged_df[["email", "role", "login_count", "resumes_processed", "timestamp"]]
                merged_df.columns = ["Email", "Role", "Usage Count", "Resumes Processed", "Timestamp"]
                st.dataframe(merged_df)
                csv_content = merged_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Analytics CSV",
                    data=csv_content,
                    file_name="user_usage_analytics.csv",
                    mime="text/csv"
                )
            st.write("### Overview")
            col1, col2 = st.columns(2)
            with col1:
                total_resumes = df_usage["resumes_processed"].sum() if "resumes_processed" in df_usage.columns else 0
                st.metric("Total Resumes Processed", total_resumes)
            with col2:
                unique_users = df_usage["user_email"].nunique() if "user_email" in df_usage.columns else 0
                st.metric("Distinct Users", unique_users)
        elif admin_option == "Resume Evaluation":
            display_resume_dashboard()
