"""
Module: authentication
Purpose: Manages user login, logout, and related Firebase operations.

"""

import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from datetime import datetime

# Identify the base directory and configuration folder.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_folder = os.path.join(BASE_DIR, "config")

# Construct path for the Firebase configuration and initialize Firebase.
firebase_path = os.path.join(config_folder, "firebase.json")
if not os.path.exists(firebase_path):
    raise FileNotFoundError(f"Firebase configuration not found at {firebase_path}")
firebase_credentials = credentials.Certificate(firebase_path)
firebase_admin.initialize_app(firebase_credentials)
firestore_db = firestore.client()

# Construct path for the OAuth configuration and initialize the OAuth flow.
oauth_path = os.path.join(config_folder, "client_secret.json")
if not os.path.exists(oauth_path):
    raise FileNotFoundError(f"OAuth configuration not found at {oauth_path}")
oauth_flow = Flow.from_client_secrets_file(
    oauth_path,
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_uri="http://localhost:8501"
)

def login_user():
    """
    Handles user login via OAuth. Redirects users to Google sign-in if authentication code is absent.
    
    Returns:
        tuple: (Boolean login status, user details dictionary or None)
    """
    if st.session_state.get("logged_in", False):
        return True, st.session_state.user_details
    query_params = st.query_params
    if "code" not in query_params:
        st.markdown(
            """
            <div style="text-align: center;">
                <h1>Welcome to SkillSync AI</h1>
                <p>Please log in to continue</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        auth_link, _ = oauth_flow.authorization_url(prompt="consent")
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
                <a href='{auth_link}' style='text-decoration: none;'>
                    <button style='background: #4285F4; color: #fff; border: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; cursor: pointer;'>
                        Sign in with Google
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        return False, None
    try:
        code_received = query_params["code"]
        oauth_flow.fetch_token(code=code_received)
        credentials_obj = oauth_flow.credentials
        verified_info = id_token.verify_oauth2_token(credentials_obj.id_token, Request())
        if not verified_info["email"].endswith("@companyemail.com"):
            st.error("Access restricted to @companyemail.com email addresses.")
            return False, None
        st.success(f"Authenticated as: {verified_info['name']} ({verified_info['email']})")
        user_ref = firestore_db.collection("users").document(verified_info['email'])
        snapshot = user_ref.get()
        if not snapshot.exists:
            user_ref.set({
                "name": verified_info['name'],
                "email": verified_info['email'],
                "profile_picture": verified_info.get("picture", ""),
                "role": "user",
                "total_resumes": 0,
                "login_count": 0
            })
        user_data = user_ref.get().to_dict()
        st.session_state.logged_in = True
        st.session_state.user_details = user_data
        st.session_state.user_role = user_data.get("role", "user")
        st.rerun()
        return True, user_data
    except Exception as error:
        st.error(f"Authentication error: {error}")
        return False, None

def log_usage(email, count):
    """
    Logs the usage count into Firestore and updates the user's document.
    
    Args:
        email (str): The user's email address.
        count (int): Number of resumes processed.
    """
    log_entry = firestore_db.collection("usage_logs").document()
    log_entry.set({
        "user_email": email,
        "resumes_processed": count,
        "timestamp": datetime.now()
    })
    user_doc = firestore_db.collection("users").document(email)
    user_doc.update({
        "total_resumes": firestore.Increment(count),
        "login_count": firestore.Increment(1)
    })

def logout_user():
    """
    Logs out the user by clearing session states and reinitializes OAuth flow.
    """
    st.session_state.logged_in = False
    st.session_state.user_details = None
    st.session_state.user_role = None
    st.session_state.token = None
    st.session_state.code = None
    st.query_params.clear()
    global oauth_flow
    oauth_flow = Flow.from_client_secrets_file(
        oauth_path,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        redirect_uri="http://localhost:8501"
    )
    st.rerun()
