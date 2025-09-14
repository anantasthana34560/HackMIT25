import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from database import TravelDatabase
import plotly.graph_objects as go
from PIL import Image
import io
import requests

# Configure Streamlit page
st.set_page_config(
    page_title="Co-Z - Your AI-Powered Travel Companion",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for light mode
st.markdown("""
<style>
    /* Light mode theme */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
        color: #212529;
    }
    
    /* Main content styling */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    
    /* Buttons - Neutral design (no blue highlight) */
    .stButton > button {
        background: #ffffff !important;
        color: #212529 !important;
        border: 1.5px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
        transition: background .2s ease, border-color .2s ease, box-shadow .2s ease, transform .05s ease !important;
    }
    
    .stButton > button:hover {
        background: #f8f9fa !important;
        border-color: #ced4da !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
        transform: translateY(-1px) !important;
        color: #212529 !important;
    }
    
    /* Form submit buttons */
    .stFormSubmitButton > button {
        background: #ffffff !important;
        color: #212529 !important;
        border: 1.5px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
        transition: background .2s ease, border-color .2s ease, box-shadow .2s ease, transform .05s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #f8f9fa !important;
        border-color: #ced4da !important;
        color: #212529 !important;
    }
    
    /* Base buttons reset */
    button {
        background: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 6px !important;
    }
    
    button:hover {
        background: #f8f9fa !important;
        color: #212529 !important;
        border-color: #ced4da !important;
    }

    /* Focus and active states (neutral) */
    .stButton > button:focus, .stFormSubmitButton > button:focus, button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.08) !important;
        border-color: #adb5bd !important;
    }
    .stButton > button:active, .stFormSubmitButton > button:active, button:active {
        background: #e9ecef !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.08) !important;
        transform: translateY(0) !important;
    }
    
    /* Form inputs - More specific targeting */
    .stTextInput > div > div > input {
        background: white !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        color: #495057 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007bff !important;
        box-shadow: 0 0 8px rgba(0, 123, 255, 0.2) !important;
        background: white !important;
    }
    
    .stSelectbox > div > div > div {
        background: white !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        color: #495057 !important;
    }
    
    .stTextArea > div > div > textarea {
        background: white !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        color: #495057 !important;
    }
    
    /* Fix input containers */
    .stTextInput > div {
        background: transparent !important;
    }
    
    .stSelectbox > div {
        background: transparent !important;
    }
    
    .stTextArea > div {
        background: transparent !important;
    }
    
    /* Fix input wrappers */
    input[type="text"], input[type="email"], input[type="password"], input[type="number"] {
        background: white !important;
        color: #495057 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    textarea {
        background: white !important;
        color: #495057 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    select {
        background: white !important;
        color: #495057 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 2px solid #e9ecef;
        padding: 0;
        border-radius: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #6c757d;
        font-weight: 400;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 0;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: transparent !important;
        color: #495057;
        border-bottom: 3px solid #dee2e6;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #212529 !important;
        border-bottom: 3px solid #495057 !important;
        font-weight: 700 !important;
    }
    
    /* Success and error messages */
    .stSuccess {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Headers and text */
    h1, h2, h3 {
        color: #212529;
    }
    
    /* Fix all text colors */
    .stMarkdown, .stText, p, span, div {
        color: #212529 !important;
    }
    
    /* Fix metric boxes */
    .metric-container {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix info boxes */
    .stAlert {
        background: white !important;
        color: #212529 !important;
        border: 1px solid #dee2e6;
    }
    
    /* Fix expander */
    .streamlit-expanderHeader {
        background: white !important;
        color: #212529 !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix columns and containers */
    .element-container {
        background: transparent !important;
    }
    
    /* Fix any remaining dark elements */
    [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    
    [data-testid="column"] {
        background: transparent !important;
    }
    
    /* Fix form containers */
    .stForm {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Fix radio buttons */
    .stRadio > div {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix checkboxes */
    .stCheckbox > div {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix date input */
    .stDateInput > div > div > input {
        background: white !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    /* Fix date input calendar popup */
    .stDateInput [data-baseweb="calendar"] {
        background: white !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
    }
    
    .stDateInput [data-baseweb="calendar"] * {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix calendar header */
    .stDateInput [data-baseweb="calendar-header"] {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix calendar days */
    .stDateInput [data-baseweb="day"] {
        background: white !important;
        color: #212529 !important;
    }
    
    .stDateInput [data-baseweb="day"]:hover {
        background: #f8f9fa !important;
        color: #212529 !important;
    }
    
    /* Fix selected date */
    .stDateInput [data-baseweb="day"][aria-selected="true"] {
        background: #007bff !important;
        color: white !important;
    }
    
    /* Fix date input container */
    .stDateInput > div {
        background: transparent !important;
    }
    
    /* Fix any remaining calendar elements */
    [data-testid="stDateInput"] {
        background: white !important;
    }
    
    [data-testid="stDateInput"] * {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix multiselect and selectbox dropdown styling */
    .stMultiSelect > div > div {
        background: white !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect > div > div > div {
        background: white !important;
        color: #212529 !important;
    }
    
    .stMultiSelect [data-baseweb="select"] {
        background: white !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
    }
    
    .stMultiSelect [data-baseweb="select"] > div {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix selectbox dropdown */
    .stSelectbox > div {
        background: white !important;
    }
    
    .stSelectbox > div > div {
        background: white !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background: white !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background: white !important;
        color: #212529 !important;
    }
    
    .stSelectbox [data-baseweb="select"] input {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix dropdown menus */
    [data-baseweb="popover"] {
        background: white !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    [data-baseweb="menu"] {
        background: white !important;
        color: #212529 !important;
    }
    
    [data-baseweb="menu-item"] {
        background: white !important;
        color: #212529 !important;
        padding: 8px 12px !important;
    }
    
    [data-baseweb="menu-item"]:hover {
        background: #f8f9fa !important;
        color: #212529 !important;
    }
    
    /* Fix specific dropdown text visibility */
    .stSelectbox div[data-testid="stSelectbox"] > div > div {
        background: white !important;
        color: #212529 !important;
    }
    
    .stSelectbox div[data-testid="stSelectbox"] > div > div > div {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Fix tags in multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background: #007bff !important;
        color: white !important;
    }
    
    /* Fix labels and help text */
    .stMultiSelect label, .stSelectbox label {
        color: #212529 !important;
    }
    
    /* Fix any remaining dark containers */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    /* Fix slider styling */
    .stSlider > div > div > div {
        background: white !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        background: white !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
    }

    /* --- Dropdown (selectbox, multiselect) menu and options visibility fix --- */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="menu"],
    .stSelectbox [data-baseweb="menu-item"],
    .stMultiSelect [data-baseweb="select"],
    .stMultiSelect [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] input,
    .stMultiSelect [data-baseweb="menu"],
    .stMultiSelect [data-baseweb="menu-item"] {
        background: #fff !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
    }

    .stSelectbox [data-baseweb="menu-item"]:hover,
    .stMultiSelect [data-baseweb="menu-item"]:hover {
        background: #e3f2fd !important;
        color: #212529 !important;
    }

    [data-baseweb="popover"] {
        background: #fff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    [data-baseweb="menu"] {
        background: #fff !important;
        color: #212529 !important;
    }
    [data-baseweb="menu-item"] {
        background: #fff !important;
        color: #212529 !important;
        padding: 8px 12px !important;
    }
    [data-baseweb="menu-item"]:hover {
        background: #e3f2fd !important;
        color: #212529 !important;
    }

    /* Nuclear option - force all elements to be visible */
    * {
        color: #212529 !important;
    }
    
    div, span, p, input, select, option {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Streamlit specific overrides */
    .stSelectbox *, .stMultiSelect *, .stDateInput * {
        background: white !important;
        color: #212529 !important;
    }
    
    /* Force dropdown visibility */
    [class*="select"], [class*="Select"], [class*="dropdown"] {
        background: white !important;
        color: #212529 !important;
    }
    
    [class*="select"] *, [class*="Select"] *, [class*="dropdown"] * {
        background: white !important;
        color: #212529 !important;
    }
            
            /* ...existing CSS... */

    /* --- Calendar (date input) improvements --- */
    .stDateInput [data-baseweb="calendar"] {
        background: #fff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
    }
    .stDateInput [data-baseweb="calendar"] * {
        background: #fff !important;
        color: #212529 !important;
    }

    /* Remove black/gray slots for days outside current month */
    .stDateInput [data-baseweb="day"][aria-disabled="true"] {
        background: #f8f9fa !important;
        color: #adb5bd !important;
        opacity: 0.6 !important;
    }

    /* Change selected date circle to a more engaging color */
    .stDateInput [data-baseweb="day"][aria-selected="true"] {
        background: #ff9800 !important;   /* Orange, eye-catching */
        color: #fff !important;
        border-radius: 50% !important;
        box-shadow: 0 0 0 2px #ff980033 !important;
        font-weight: bold !important;
        outline: none !important;
    }
            
                /* --- Calendar (date input) improvements --- */
    .stDateInput [data-baseweb="calendar"] {
        background: #fff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
    }
    .stDateInput [data-baseweb="calendar"] * {
        background: #fff !important;
        color: #212529 !important;
    }

    /* Remove black/gray slots for days outside current month */
    .stDateInput [data-baseweb="day"][aria-disabled="true"] {
        background: #f8f9fa !important;
        color: #adb5bd !important;
        opacity: 0.6 !important;
    }

    /* Change selected date circle to a more engaging color */
    .stDateInput [data-baseweb="day"][aria-selected="true"] {
        background: #ff9800 !important;   /* Orange, eye-catching */
        color: #fff !important;
        border-radius: 50% !important;
        box-shadow: 0 0 0 2px #ff980033 !important;
        font-weight: bold !important;
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

class TravelEaseApp:
    def __init__(self):
        self.db = TravelDatabase()
        self.init_session_state()

    def init_session_state(self):
        """Initialize session state variables"""
        # User account and profile
        if 'user_registered' not in st.session_state:
            st.session_state.user_registered = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {}

        # Travel planning steps
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 'landing'
        if 'travel_plans' not in st.session_state:
            st.session_state.travel_plans = {}
        if 'selected_destination' not in st.session_state:
            st.session_state.selected_destination = {}
        if 'selected_transport' not in st.session_state:
            st.session_state.selected_transport = {}
        if 'selected_accommodation' not in st.session_state:
            st.session_state.selected_accommodation = {}
        if 'selected_restaurants' not in st.session_state:
            st.session_state.selected_restaurants = []
        if 'selected_experiences' not in st.session_state:
            st.session_state.selected_experiences = []
        if 'final_itinerary' not in st.session_state:
            st.session_state.final_itinerary = {}

        # Host interface
        if 'is_host' not in st.session_state:
            st.session_state.is_host = False
        if 'host_properties' not in st.session_state:
            st.session_state.host_properties = []

    def make_api_request(self, endpoint, data=None):
        """Make API request to Flask backend"""
        try:
            if data:
                response = requests.post(f"{API_BASE_URL}{endpoint}", json=data)
            else:
                response = requests.get(f"{API_BASE_URL}{endpoint}")
            return response.json()
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to backend. Please make sure the Flask server is running on port 5000.")
            return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def render_landing_page(self):
        """Render the landing page with user registration"""
        # Logo and branding header
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0 2rem 0;'>
            <div style='margin-bottom: 2rem;'>
                <div style='display: inline-block; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                    <div style='font-size: 4rem; color: #E67E22; margin-bottom: 10px;'>🏠</div>
                </div>
            </div>
            <h1 style='color: #E67E22; font-size: 3.5rem; margin-bottom: 1rem; font-weight: 700;'>Co-Z</h1>
            <h2 style='color: #424242; font-weight: 300; margin-bottom: 2rem;'>Your AI-Powered Travel Companion</h2>
            <p style='font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto;'>
                Plan your accommodation and everything from flights to restaurants and experiences - all in one place!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Add tabs for Login vs Register
            tab1, tab2 = st.tabs(["🔑 Sign In", "🚀 Create Account"])

            with tab1:
                st.markdown("### Welcome Back!")

                with st.form("user_login"):
                    email_login = st.text_input("Email Address")
                    password_login = st.text_input("Password", type="password")

                    login_submitted = st.form_submit_button("Sign In", use_container_width=True)

                    if login_submitted:
                        if not email_login or not password_login:
                            st.error("Please enter both email and password")
                        else:
                            user = self.db.authenticate_user(email_login, password_login)
                            if user:
                                # Load user data into session
                                st.session_state.user_id = user['id']
                                st.session_state.user_profile = user
                                st.session_state.user_registered = True

                                # Load user preferences
                                preferences = self.db.get_user_preferences(user['id'])
                                if preferences:
                                    st.session_state.user_preferences = preferences
                                    st.session_state.current_step = 'step1'
                                else:
                                    st.session_state.current_step = 'preferences'

                                st.success(f"Welcome back, {user['first_name']}!")
                                st.rerun()
                            else:
                                st.error("Invalid email or password")

            with tab2:
                st.markdown("### Create Your Account")

                with st.form("user_registration"):
                    st.markdown("**Personal Information**")
                    col_a, col_b = st.columns(2)

                    with col_a:
                        first_name = st.text_input("First Name*")
                        email = st.text_input("Email Address*")
                        phone = st.text_input("Phone Number")

                    with col_b:
                        last_name = st.text_input("Last Name*")
                        password = st.text_input("Password*", type="password")
                    confirm_password = st.text_input("Confirm Password*", type="password")

                    date_of_birth = st.date_input("Date of Birth*", min_value=date(1900, 1, 1), max_value=date.today())
                    address = st.text_area("Address")

                    col_c, col_d = st.columns(2)
                    with col_c:
                        city = st.text_input("City*")
                        country = st.selectbox("Country*", [
                            "United States", "Canada", "United Kingdom", "Australia", "Germany",
                            "France", "Spain", "Italy", "Japan", "Other"
                        ])

                    with col_d:
                        state_province = st.text_input("State/Province")
                        postal_code = st.text_input("Postal Code")

                    emergency_contact = st.text_input("Emergency Contact Name")
                    emergency_phone = st.text_input("Emergency Contact Phone")

                    # Account type selection
                    st.markdown("**Account Type**")
                    account_type = st.radio(
                        "I want to:",
                        ["Plan and book travel (Traveler)", "List my property for rent (Host)", "Both"]
                    )

                    submitted = st.form_submit_button("Create Account", use_container_width=True)

                if submitted:
                    if not all([first_name, last_name, email, password, confirm_password, city, country]):
                        st.error("Please fill in all required fields marked with *")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        # Create user in database
                        user_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'password': password,
                            'phone': phone,
                            'date_of_birth': date_of_birth,
                            'address': address,
                            'city': city,
                            'state_province': state_province,
                            'country': country,
                            'postal_code': postal_code,
                            'emergency_contact': emergency_contact,
                            'emergency_phone': emergency_phone,
                            'account_type': account_type
                        }

                        user_id = self.db.create_user(user_data)

                        if user_id:
                            # Save to session state
                            st.session_state.user_id = user_id
                            st.session_state.user_profile = {
                                'first_name': first_name,
                                'last_name': last_name,
                                'email': email,
                                'city': city,
                                'country': country,
                                'account_type': account_type
                            }

                            if "Host" in account_type:
                                st.session_state.is_host = True

                            st.session_state.user_registered = True
                            st.session_state.current_step = 'preferences'
                            st.success("Account created successfully! Let's learn more about your travel preferences.")
                            st.rerun()
                        else:
                            st.error("Email already exists. Please use a different email address.")

    def render_preferences_page(self):
        """Render the user preferences and lifestyle information page"""
        st.markdown(f"### 👋 Welcome, {st.session_state.user_profile['first_name']}!")
        st.markdown("#### Tell us more about yourself to personalize your travel experience")

        with st.form("preferences_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Travel Experience**")
                age_group = st.selectbox("Age Group", [
                    "18-25", "26-35", "36-45", "46-55", "56-65", "65+"
                ])

                travel_frequency = st.selectbox("How often do you travel?", [
                    "First time traveler", "Once a year", "2-3 times a year",
                    "4-6 times a year", "More than 6 times a year", "I'm a digital nomad"
                ])

                budget_range = st.selectbox("Typical travel budget per trip", [
                    "Under $500", "$500 - $1,500", "$1,500 - $3,000",
                    "$3,000 - $5,000", "$5,000 - $10,000", "$10,000+"
                ])

                group_preference = st.multiselect("Who do you usually travel with?", [
                    "Solo", "Partner/Spouse", "Family with kids", "Friends",
                    "Extended family", "Business colleagues", "Tour groups"
                ])

            with col2:
                st.markdown("**Travel Preferences**")
                vacation_style = st.multiselect("Preferred vacation style", [
                    "Relaxing/Beach", "Adventure/Active", "Cultural/Historical",
                    "City exploration", "Nature/Wildlife", "Food & Wine",
                    "Nightlife/Entertainment", "Wellness/Spa", "Business travel"
                ])

                accommodation_type = st.multiselect("Preferred accommodation types", [
                    "Hotels", "Entire house", "Apartment", "Condo/Townhouse",
                    "Private room", "Shared room", "Hostels", "Resorts",
                    "Boutique hotels", "Bed & Breakfast", "Villa", "Cabin/Cottage",
                    "Camping", "Luxury accommodations", "Unique stays (treehouse, boat, etc.)"
                ])

                location_preferences = st.multiselect("Preferred destinations", [
                    "Beach/Coastal", "Mountains", "Cities", "Countryside",
                    "Tropical islands", "Desert", "Forest/National parks",
                    "Historical sites", "Modern metropolis"
                ])

                transport_preference = st.multiselect("Preferred transportation", [
                    "Flying", "Driving/Road trips", "Train travel", "Cruises",
                    "Public transportation", "Walking/Biking", "Ride sharing"
                ])

            st.markdown("**Lifestyle & Interests**")
            col3, col4 = st.columns(2)

            with col3:
                dietary_restrictions = st.multiselect("Dietary restrictions/preferences", [
                    "None", "Vegetarian", "Vegan", "Gluten-free", "Halal",
                    "Kosher", "Dairy-free", "Nut allergies", "Other food allergies"
                ])

                interests = st.multiselect("Interests & hobbies", [
                    "Photography", "Art & Museums", "Music & Concerts", "Sports",
                    "Hiking", "Water sports", "Shopping", "Cooking classes",
                    "Local festivals", "Architecture", "Wildlife watching"
                ])

            with col4:
                accessibility_needs = st.multiselect("Accessibility requirements", [
                    "None", "Wheelchair accessible", "Mobility assistance",
                    "Visual impairment support", "Hearing impairment support",
                    "Other special needs"
                ])

                language_preferences = st.multiselect("Languages you speak", [
                    "English", "Spanish", "French", "German", "Italian",
                    "Portuguese", "Mandarin", "Japanese", "Arabic", "Other"
                ])

            submitted = st.form_submit_button("Save Preferences & Continue", use_container_width=True)

            if submitted:
                preferences = {
                    'age_group': age_group,
                    'travel_frequency': travel_frequency,
                    'budget_range': budget_range,
                    'group_preference': group_preference,
                    'vacation_style': vacation_style,
                    'accommodation_type': accommodation_type,
                    'location_preferences': location_preferences,
                    'transport_preference': transport_preference,
                    'dietary_restrictions': dietary_restrictions,
                    'interests': interests,
                    'accessibility_needs': accessibility_needs,
                    'language_preferences': language_preferences
                }

                # Save to database
                if st.session_state.user_id:
                    self.db.save_user_preferences(st.session_state.user_id, preferences)

                st.session_state.user_preferences = preferences
                st.session_state.current_step = 'step1'
                st.success("Preferences saved! Let's start planning your perfect trip.")
                st.rerun()

    def render_step1_travel_wishes(self):
        """Step 1: Adventure destination chat interface"""
        # Header with logo and travel theme
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <div style='margin-bottom: 1.5rem;'>
                <div style='display: inline-block; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                    <div style='font-size: 3rem; color: #E67E22;'>🏠</div>
                </div>
            </div>
            <h1 style='color: #007bff; font-size: 2.5rem; margin-bottom: 1rem;'>
                🌟 Hello! Where would you like your next adventure to take place?
            </h1>
            <p style='font-size: 1.2rem; color: #6c757d; margin-bottom: 2rem;'>
                Tell us about your dream destination in your own words - be as detailed or as brief as you'd like!
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("adventure_destination"):
            # Main text area for user input
            destination_description = st.text_area(
                "",
                placeholder="Describe your ideal travel destination... Where do you want to go? What kind of experience are you looking for?",
                height=150,
                help="Share your travel dreams, preferences, and any specific requirements you have in mind."
            )
            
            # Ideas section below the text area
            st.markdown("""
            <div style='background: rgba(0, 123, 255, 0.05); padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                <h4 style='color: #007bff; margin-bottom: 0.5rem;'>💡 Ideas to get you started:</h4>
                <p style='color: #6c757d; margin: 0; line-height: 1.6;'>
                    <strong>Location:</strong> specific cities, countries, regions, or "surprise me!"<br>
                    <strong>Cuisine:</strong> local food experiences, cooking classes, food tours<br>
                    <strong>Pet-friendly:</strong> traveling with furry companions<br>
                    <strong>Urban vs Rural:</strong> bustling cities or peaceful countryside<br>
                    <strong>Transportation:</strong> access to public transit, walkable areas<br>
                    <strong>Activities:</strong> beaches, mountains, museums, nightlife, adventure sports<br>
                    <strong>Accommodation:</strong> hotels, vacation rentals, unique stays<br>
                    <strong>Budget:</strong> luxury, mid-range, or budget-friendly options<br>
                    <strong>Travel style:</strong> relaxing, adventurous, cultural, romantic
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Additional quick options
            col1, col2 = st.columns(2)
            
            with col1:
                trip_duration = st.selectbox("How long is your trip?", [
                    "Weekend (2-3 days)", "Short trip (4-7 days)",
                    "Week-long (8-14 days)", "Extended (2-4 weeks)", "Month or longer"
                ])
                
            with col2:
                travel_dates = st.date_input(
                    "Preferred travel dates (optional)",
                    value=None,
                    help="Leave blank if you're flexible with dates"
                )

            submitted = st.form_submit_button("✈️ Let's Plan My Adventure!", use_container_width=True)

            if submitted:
                if not destination_description.strip():
                    st.error("Please tell us about your dream destination!")
                else:
                    st.session_state.travel_plans = {
                        'destination_description': destination_description,
                        'trip_duration': trip_duration,
                        'travel_dates': travel_dates if travel_dates else None
                    }

                    st.session_state.current_step = 'step2'
                    st.success("Great! Let's find the perfect destination for you.")
                    st.rerun()

    def render_step2_destination(self):
        """Step 2: Destination and timeframe selection"""
        st.markdown("## 🗺️ Step 2: Where You're Traveling To")
        st.markdown("Let's confirm your destination and timeframe!")

        # Show AI-generated destination suggestions based on user input
        destination_input = st.session_state.travel_plans.get('destination_input', '')

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Destination Recommendations")

            # Get AI-powered destination suggestions from Flask backend
            with st.spinner("🤖 Getting AI-powered destination recommendations..."):
                # Prepare the travel preferences for the AI (convert dates to strings for JSON serialization)
                travel_plans_serializable = dict(st.session_state.travel_plans)
                if 'travel_dates' in travel_plans_serializable:
                    travel_plans_serializable['travel_dates'] = [
                        date.isoformat() if hasattr(date, 'isoformat') else str(date)
                        for date in travel_plans_serializable['travel_dates']
                    ]

                travel_preferences = {
                    'destination_input': destination_input,
                    'user_preferences': st.session_state.user_preferences,
                    'travel_plans': travel_plans_serializable
                }

                # Call the Flask backend for AI recommendations
                ai_result = self.make_api_request("/ai-agent", {
                    "query": f"I want to travel to {destination_input}. Suggest 3 specific destinations with details including name, description, best time to visit, and average temperature.",
                    "preferences": travel_preferences
                })

                if ai_result and ai_result.get('success') and ai_result.get('recommendations'):
                    # Use AI-generated recommendations
                    suggested_destinations = []
                    for rec in ai_result['recommendations'][:3]:  # Take top 3
                        suggested_destinations.append({
                            "name": rec.get('name', 'Unknown Destination'),
                            "description": rec.get('description', 'A wonderful travel destination'),
                            "best_time": rec.get('best_time', 'Year-round'),
                            "avg_temp": rec.get('avg_temp', 'Varies')
                        })
                    st.success("✨ AI-powered recommendations generated!")
                else:
                    # Fallback to contextual suggestions if AI fails
                    st.warning("AI recommendations unavailable. Using curated suggestions.")
                    if 'france' in destination_input.lower():
                        suggested_destinations = [
                            {"name": "Paris, France", "description": "City of Light with world-class museums, cuisine, and romance", "best_time": "April-June, September-October", "avg_temp": "15-25°C", "image_url": "https://images.unsplash.com/photo-1502602898536-47ad22581b52?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Nice, France", "description": "French Riviera with stunning beaches and Mediterranean charm", "best_time": "May-September", "avg_temp": "18-28°C", "image_url": "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Lyon, France", "description": "Gastronomic capital with Renaissance architecture", "best_time": "April-October", "avg_temp": "12-26°C", "image_url": "https://images.unsplash.com/photo-1524396309943-e03f5249f002?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"}
                        ]
                    elif 'italy' in destination_input.lower():
                        suggested_destinations = [
                            {"name": "Rome, Italy", "description": "Eternal City with ancient history and incredible cuisine", "best_time": "April-June, September-October", "avg_temp": "15-25°C", "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Florence, Italy", "description": "Renaissance art and architecture in Tuscany", "best_time": "April-June, September-October", "avg_temp": "15-25°C", "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Venice, Italy", "description": "Romantic canals and unique island city", "best_time": "April-June, September-October", "avg_temp": "15-25°C", "image_url": "https://images.unsplash.com/photo-1514890547357-a9ee288728e0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"}
                        ]
                    elif 'india' in destination_input.lower():
                        suggested_destinations = [
                            {"name": "Mumbai, India", "description": "Financial capital with Bollywood glamour and incredible street food", "best_time": "November-March", "avg_temp": "20-32°C", "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Delhi, India", "description": "Historic capital with Mughal architecture and vibrant markets", "best_time": "October-March", "avg_temp": "15-30°C", "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Goa, India", "description": "Tropical paradise with pristine beaches and Portuguese heritage", "best_time": "November-February", "avg_temp": "23-32°C", "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"}
                        ]
                    else:
                        # Generic popular destinations
                        suggested_destinations = [
                            {"name": "Paris, France", "description": "City of Light with world-class museums, cuisine, and romance", "best_time": "April-June, September-October", "avg_temp": "15-25°C", "image_url": "https://images.unsplash.com/photo-1502602898536-47ad22581b52?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "Tokyo, Japan", "description": "Modern metropolis blending tradition with cutting-edge technology", "best_time": "March-May, September-November", "avg_temp": "10-26°C", "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"},
                            {"name": "New York City, USA", "description": "The city that never sleeps with iconic landmarks", "best_time": "April-June, September-November", "avg_temp": "10-25°C", "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"}
                        ]

            # Initialize swipe session state
            if 'current_destination_index' not in st.session_state:
                st.session_state.current_destination_index = 0
            if 'liked_destinations' not in st.session_state:
                st.session_state.liked_destinations = []
            if 'rejected_destinations' not in st.session_state:
                st.session_state.rejected_destinations = []

            # Check if we have destinations to show
            if st.session_state.current_destination_index < len(suggested_destinations):
                current_dest = suggested_destinations[st.session_state.current_destination_index]

                # Create swipe card interface
                st.markdown("### 💫 Swipe to Choose Your Destination")
                st.markdown("❤️ **Swipe Right (Like)** if you're interested | 💔 **Swipe Left (Pass)** if not for you")

                # Destination card
                with st.container():
                    # Get image URL, fallback to a default if not available
                    image_url = current_dest.get('image_url', 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80')

                    # Display image using Streamlit's native method
                    st.image(image_url, width=400)

                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 2rem;
                        border-radius: 0 0 20px 20px;
                        color: white;
                        text-align: center;
                        margin-top: -5px;
                    ">
                        <h2 style="margin: 0 0 1rem 0; font-size: 2rem;">📍 {current_dest['name']}</h2>
                        <p style="font-size: 1.2rem; margin: 1rem 0; line-height: 1.6;">{current_dest['description']}</p>
                        <div style="display: flex; justify-content: space-around; margin-top: 1.5rem; flex-wrap: wrap;">
                            <div style="margin: 0.5rem;">
                                <strong>🌡️ Temperature:</strong><br>{current_dest['avg_temp']}
                            </div>
                            <div style="margin: 0.5rem;">
                                <strong>📅 Best Time:</strong><br>{current_dest['best_time']}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Swipe buttons
                col_left, col_center, col_right = st.columns([1, 1, 1])

                with col_left:
                    if st.button("👎 Pass", use_container_width=True, type="secondary"):
                        st.session_state.rejected_destinations.append(current_dest)
                        st.session_state.current_destination_index += 1
                        st.rerun()

                with col_right:
                    if st.button("❤️ Like", use_container_width=True, type="primary"):
                        st.session_state.liked_destinations.append(current_dest)
                        st.session_state.current_destination_index += 1
                        st.rerun()

                # Progress indicator
                progress = (st.session_state.current_destination_index + 1) / len(suggested_destinations)
                st.progress(progress)
                st.caption(f"Destination {st.session_state.current_destination_index + 1} of {len(suggested_destinations)}")

            else:
                # Show results after swiping through all destinations
                st.markdown("### 🎉 Swipe Complete!")

                if st.session_state.liked_destinations:
                    st.markdown("#### ❤️ Your Liked Destinations:")
                    for dest in st.session_state.liked_destinations:
                        with st.expander(f"📍 {dest['name']}", expanded=True):
                            st.write(dest['description'])
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"🌡️ **Temperature:** {dest['avg_temp']}")
                            with col2:
                                st.write(f"📅 **Best Time:** {dest['best_time']}")

                    # Let user select final destination from liked ones
                    st.markdown("#### 🎯 Choose Your Final Destination:")
                    selected_dest_name = st.selectbox(
                        "Which destination would you like to visit?",
                        options=[dest["name"] for dest in st.session_state.liked_destinations],
                        format_func=lambda x: f"📍 {x}"
                    )
                    selected_dest_info = next(dest for dest in st.session_state.liked_destinations if dest["name"] == selected_dest_name)

                else:
                    st.warning("You didn't like any destinations! Let's try again with different options.")
                    if st.button("🔄 Reset and Try Again"):
                        st.session_state.current_destination_index = 0
                        st.session_state.liked_destinations = []
                        st.session_state.rejected_destinations = []
                        st.rerun()
                    return

                # Reset button
                if st.button("🔄 Start Over with Swipes"):
                    st.session_state.current_destination_index = 0
                    st.session_state.liked_destinations = []
                    st.session_state.rejected_destinations = []
                    st.rerun()

            # Set variables for the navigation section
            if st.session_state.liked_destinations and st.session_state.current_destination_index >= len(suggested_destinations):
                # User has completed swiping and selected a final destination
                selected_dest = selected_dest_name
                selected_dest_info = next(dest for dest in st.session_state.liked_destinations if dest["name"] == selected_dest_name)

                st.info(f"""
                **{selected_dest_info['name']}**

                {selected_dest_info['description']}

                🌡️ **Average Temperature:** {selected_dest_info['avg_temp']}
                📅 **Best Time to Visit:** {selected_dest_info['best_time']}
                """)
            else:
                # User is still swiping or hasn't liked any destinations
                selected_dest = None
                selected_dest_info = None

        with col2:
            st.markdown("### 📅 Timeframe Details")

            travel_dates = st.session_state.travel_plans.get('travel_dates', [date.today(), date.today()])
            trip_duration = st.session_state.travel_plans.get('trip_duration', '')

            st.write(f"**Duration:** {trip_duration}")
            st.write(f"**Dates:** {travel_dates[0]} to {travel_dates[-1] if len(travel_dates) > 1 else travel_dates[0]}")

            # Allow modifications
            modify_dates = st.checkbox("Modify dates/duration")

            if modify_dates:
                new_dates = st.date_input("New travel dates", value=travel_dates)
                new_duration = st.selectbox("New duration", [
                    "Weekend (2-3 days)", "Short trip (4-7 days)",
                    "Week-long (8-14 days)", "Extended (2-4 weeks)", "Month or longer"
                ])

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            if st.button("← Back to Travel Wishes", use_container_width=True):
                st.session_state.current_step = 'step1'
                st.rerun()

        with col4:
            if st.button("Continue to Accommodation →", use_container_width=True):
                if selected_dest and selected_dest_info:
                    st.session_state.selected_destination = {
                        'name': selected_dest,
                        'info': selected_dest_info,
                        'dates': new_dates if 'new_dates' in locals() and modify_dates else travel_dates,
                        'duration': new_duration if 'new_duration' in locals() and modify_dates else trip_duration
                    }
                    st.session_state.current_step = 'step3'
                    st.success(f"Destination set: {selected_dest}")
                    st.rerun()
                else:
                    st.error("Please complete the destination selection by swiping through all options and choosing a final destination.")

    # COMMENTED OUT - Step 3: Transportation/How to get there
    def render_step3_transportation(self):
        """Step 3: Transportation/How to get there - COMMENTED OUT"""
        # Automatically skip to accommodation without showing any UI
        st.session_state.selected_transport = {}
        st.session_state.current_step = 'step4'
        st.rerun()

        # COMMENTED OUT - All transportation content
        # destination = st.session_state.selected_destination.get('name', 'your destination')
        # user_location = f"{st.session_state.user_profile.get('city', '')}, {st.session_state.user_profile.get('country', '')}"

        # st.markdown(f"**From:** {user_location}")
        # st.markdown(f"**To:** {destination}")

        # # tab1, tab2, tab3 = st.tabs(["✈️ Flights", "🚗 Ground Transport", "🚢 Other Options"])
        # tab1, tab2 = st.tabs(["🚗 Ground Transport", "🚢 Other Options"])

        # # COMMENTED OUT - Flight Options
        # # with tab1:
        # #     st.markdown("### Flight Options")

        # #     # Mock flight data
        # #     flights = [
        # #         {"airline": "Delta Airlines", "departure": "8:00 AM", "arrival": "2:30 PM", "duration": "6h 30m", "stops": "Direct", "price": "$450", "class": "Economy"},
        # #         {"airline": "United Airlines", "departure": "11:15 AM", "arrival": "6:45 PM", "duration": "7h 30m", "stops": "1 stop", "price": "$380", "class": "Economy"},
        # #         {"airline": "Air France", "departure": "6:30 PM", "arrival": "11:00 AM+1", "duration": "8h 30m", "stops": "Direct", "price": "$650", "class": "Business"}
        # #     ]

        # #     selected_flight = st.radio("Choose your flight:", options=range(len(flights)), format_func=lambda i: f"{flights[i]['airline']} - {flights[i]['departure']} to {flights[i]['arrival']} ({flights[i]['duration']}) - {flights[i]['price']}")

        # #     flight_details = flights[selected_flight]
        # #     st.info(f"""
        # #     **Selected Flight Details:**
        # #     - **Airline:** {flight_details['airline']}
        # #     - **Departure:** {flight_details['departure']}
        # #     - **Arrival:** {flight_details['arrival']}
        # #     - **Duration:** {flight_details['duration']}
        # #     - **Stops:** {flight_details['stops']}
        # #     - **Class:** {flight_details['class']}
        # #     - **Price:** {flight_details['price']}
        # #     """)

        # with tab1:
        #     st.markdown("### Ground Transportation at Destination")

        #     transport_options = st.multiselect("Select transportation methods you'd like to use:", [
        #         "Airport shuttle", "Taxi/Uber", "Public transportation", "Rental car",
        #         "Hotel transfer", "Private driver", "Walking", "Bicycle rental"
        #     ])

        #     if "Rental car" in transport_options:
        #         car_type = st.selectbox("Preferred car type:", ["Economy", "Compact", "Mid-size", "Full-size", "SUV", "Luxury"])
        #         st.write(f"Car rental estimate: $35-85/day for {car_type}")

        # with tab2:
        #     st.markdown("### Alternative Transportation")

        #     other_options = st.multiselect("Other transportation options:", [
        #         "Train", "Bus", "Ferry", "Cruise", "Private jet", "Road trip"
        #     ])

        #     if other_options:
        #         st.write("We'll research these options and include them in your itinerary!")

    def render_step4_accommodation(self):
        """Step 4: Accommodation (Airbnb-style)"""
        st.markdown("## 🏠 Step 4: Your Home Away from Home")
        st.markdown("Find the perfect place to stay!")

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            property_type = st.selectbox("Property Type", [
                "Entire home/apartment", "Private room", "Hotel room", "Shared room", "Unique stays"
            ])

        with col2:
            guests = st.number_input("Number of guests", min_value=1, max_value=20, value=2)

        with col3:
            price_range = st.selectbox("Price per night", [
                "$0 - $50", "$50 - $100", "$100 - $200", "$200 - $500", "$500+"
            ])

        # Amenities
        st.markdown("### 🛋️ Desired Amenities")
        amenities = st.multiselect("Select amenities:", [
            "WiFi", "Kitchen", "Washing machine", "Air conditioning", "Heating",
            "Pool", "Hot tub", "Gym", "Parking", "Pet-friendly", "Smoking allowed",
            "Wheelchair accessible", "Laptop-friendly workspace", "TV", "Fireplace"
        ])

        # Generate more diverse property options with images
        properties = [
            {
                "title": "Cozy Downtown Apartment",
                "type": "Entire apartment",
                "guests": 4,
                "bedrooms": 2,
                "bathrooms": 1,
                "price": 85,
                "rating": 4.8,
                "reviews": 127,
                "amenities": ["WiFi", "Kitchen", "Air conditioning", "Washing machine"],
                "description": "Beautiful apartment in the heart of the city, walking distance to major attractions.",
                "host": "Sarah M.",
                "superhost": True,
                "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
            },
            {
                "title": "Luxury Villa with Pool",
                "type": "Entire villa",
                "guests": 8,
                "bedrooms": 4,
                "bathrooms": 3,
                "price": 250,
                "rating": 4.9,
                "reviews": 89,
                "amenities": ["WiFi", "Kitchen", "Pool", "Hot tub", "Parking", "Air conditioning"],
                "description": "Stunning villa with private pool and garden, perfect for families or groups.",
                "host": "Michael R.",
                "superhost": True,
                "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
            },
            {
                "title": "Budget-Friendly Private Room",
                "type": "Private room",
                "guests": 2,
                "bedrooms": 1,
                "bathrooms": 1,
                "price": 35,
                "rating": 4.6,
                "reviews": 203,
                "amenities": ["WiFi", "Shared kitchen", "Air conditioning"],
                "description": "Clean and comfortable private room with friendly hosts.",
                "host": "Anna L.",
                "superhost": False,
                "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
            },
            {
                "title": "Modern Loft with City Views",
                "type": "Entire loft",
                "guests": 6,
                "bedrooms": 3,
                "bathrooms": 2,
                "price": 180,
                "rating": 4.7,
                "reviews": 156,
                "amenities": ["WiFi", "Kitchen", "Gym", "Parking", "TV", "Workspace"],
                "description": "Stylish loft with panoramic city views and modern amenities.",
                "host": "David K.",
                "superhost": True,
                "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
            },
            {
                "title": "Charming Cottage Retreat",
                "type": "Entire cottage",
                "guests": 4,
                "bedrooms": 2,
                "bathrooms": 1,
                "price": 120,
                "rating": 4.9,
                "reviews": 78,
                "amenities": ["WiFi", "Kitchen", "Fireplace", "Garden", "Pet-friendly"],
                "description": "Peaceful cottage surrounded by nature, perfect for a relaxing getaway.",
                "host": "Emma T.",
                "superhost": False,
                "image_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
            }
        ]

        # Initialize swipe session state for accommodations
        if 'current_accommodation_index' not in st.session_state:
            st.session_state.current_accommodation_index = 0
        if 'liked_accommodations' not in st.session_state:
            st.session_state.liked_accommodations = []
        if 'rejected_accommodations' not in st.session_state:
            st.session_state.rejected_accommodations = []

        # Check if we have accommodations to show
        if st.session_state.current_accommodation_index < len(properties):
            current_prop = properties[st.session_state.current_accommodation_index]

            # Create swipe card interface for accommodations
            st.markdown("### 🏠 Swipe to Choose Your Accommodation")
            st.markdown("❤️ **Swipe Right (Like)** if you want to stay here | 💔 **Swipe Left (Pass)** if not for you")
                        # Property card
            with st.container():
                amenities_display = ", ".join(current_prop['amenities'][:4])
                if len(current_prop['amenities']) > 4:
                    amenities_display += f" + {len(current_prop['amenities']) - 4} more"

                superhost_badge = "🏆 Superhost" if current_prop['superhost'] else ""

                # Display image using Streamlit's native method
                st.image(current_prop['image_url'], width=300)

                # Use a simpler approach with native Streamlit components
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%); padding: 2rem; border-radius: 0 0 20px 20px; margin-top: -5px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                </div>
                """, unsafe_allow_html=True)

                # Use native Streamlit components for content
                col_title, col_price = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### 🏠 {current_prop['title']}")
                with col_price:
                    st.markdown(f"**${current_prop['price']}** per night")

                st.markdown(f"*{current_prop['description']}*")

                # Property details in columns
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f"**🏠 Type:** {current_prop['type']}")
                    st.markdown(f"**👥 Guests:** {current_prop['guests']} people")
                with col_b:
                    st.markdown(f"**🛏️ Bedrooms:** {current_prop['bedrooms']}")
                    st.markdown(f"**🚿 Bathrooms:** {current_prop['bathrooms']}")
                with col_c:
                    st.markdown(f"**⭐ Rating:** {current_prop['rating']} ({current_prop['reviews']} reviews)")
                    st.markdown(f"**🏡 Host:** {current_prop['host']} {superhost_badge}")

                st.markdown(f"**🛋️ Amenities:** {amenities_display}")

            # Swipe buttons
            col_left, col_center, col_right = st.columns([1, 1, 1])

            with col_left:
                if st.button("👎 Pass", use_container_width=True, type="secondary", key="accommodation_pass"):
                    st.session_state.rejected_accommodations.append(current_prop)
                    st.session_state.current_accommodation_index += 1
                    st.rerun()

            with col_right:
                if st.button("❤️ Like", use_container_width=True, type="primary", key="accommodation_like"):
                    st.session_state.liked_accommodations.append(current_prop)
                    st.session_state.current_accommodation_index += 1
                    st.rerun()

            # Progress indicator
            progress = (st.session_state.current_accommodation_index + 1) / len(properties)
            st.progress(progress)
            st.caption(f"Property {st.session_state.current_accommodation_index + 1} of {len(properties)}")

        else:
            # Show results after swiping through all accommodations
            st.markdown("### 🎉 Swipe Complete!")

            if st.session_state.liked_accommodations:
                st.markdown("#### ❤️ Your Liked Accommodations:")
                for prop in st.session_state.liked_accommodations:
                    with st.expander(f"🏠 {prop['title']} - ${prop['price']}/night", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(prop['description'])
                            st.write(f"**Host:** {prop['host']}")
                            if prop['superhost']:
                                st.write("🏆 **Superhost**")
                        with col2:
                            st.write(f"🏠 **Type:** {prop['type']}")
                            st.write(f"👥 **Guests:** {prop['guests']} people")
                            st.write(f"🛏️ **Bedrooms:** {prop['bedrooms']}")
                            st.write(f"⭐ **Rating:** {prop['rating']} ({prop['reviews']} reviews)")

                # Let user select final accommodation from liked ones
                st.markdown("#### 🎯 Choose Your Final Accommodation:")
                selected_accommodation_title = st.selectbox(
                    "Which property would you like to book?",
                    options=[prop["title"] for prop in st.session_state.liked_accommodations],
                    format_func=lambda x: f"🏠 {x}"
                )
                selected_accommodation = next(prop for prop in st.session_state.liked_accommodations if prop["title"] == selected_accommodation_title)

            else:
                st.warning("You didn't like any accommodations! Let's try again with different options.")
                if st.button("🔄 Reset and Try Again", key="accommodation_reset"):
                    st.session_state.current_accommodation_index = 0
                    st.session_state.liked_accommodations = []
                    st.session_state.rejected_accommodations = []
                    st.rerun()
                return

            # Reset button
            if st.button("🔄 Start Over with Swipes", key="accommodation_restart"):
                st.session_state.current_accommodation_index = 0
                st.session_state.liked_accommodations = []
                st.session_state.rejected_accommodations = []
                st.rerun()

        # Set variables for the navigation section
        if st.session_state.liked_accommodations and st.session_state.current_accommodation_index >= len(properties):
            # User has completed swiping and selected a final accommodation
            st.session_state.selected_accommodation = selected_accommodation

            st.success(f"✅ Selected: {selected_accommodation['title']} - ${selected_accommodation['price']}/night")
        else:
            # User is still swiping or hasn't liked any accommodations
            selected_accommodation = None

        # Navigation buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back to Accommodation", use_container_width=True):
                st.session_state.current_step = 'step3'
                st.rerun()

        with col2:
            if st.button("Continue to Dining →", use_container_width=True):
                if selected_accommodation:
                    st.session_state.current_step = 'step5'
                    st.rerun()
                else:
                    st.error("Please complete the accommodation selection by swiping through all options and choosing a final property.")

    def render_host_interface(self):
        """Host interface for adding and managing properties"""
        st.markdown("## 🏠 Host Dashboard")
        st.markdown("Manage your property listings")

        tab1, tab2, tab3 = st.tabs(["➕ Add Property", "📋 My Properties", "📊 Analytics"])

        with tab1:
            st.markdown("### Add New Property")

            with st.form("add_property"):
                col1, col2 = st.columns(2)

                with col1:
                    property_title = st.text_input("Property Title*")
                    property_type = st.selectbox("Property Type*", [
                        "Entire home/apartment", "Private room", "Shared room", "Hotel room", "Unique stay"
                    ])
                    max_guests = st.number_input("Maximum Guests*", min_value=1, max_value=20, value=2)
                    bedrooms = st.number_input("Bedrooms*", min_value=0, max_value=10, value=1)
                    bathrooms = st.number_input("Bathrooms*", min_value=1, max_value=10, value=1)

                with col2:
                    price_per_night = st.number_input("Price per Night ($)*", min_value=1, value=50)
                    cleaning_fee = st.number_input("Cleaning Fee ($)", min_value=0, value=25)
                    security_deposit = st.number_input("Security Deposit ($)", min_value=0, value=100)
                    minimum_stay = st.number_input("Minimum Stay (nights)", min_value=1, value=1)
                    maximum_stay = st.number_input("Maximum Stay (nights)", min_value=1, max_value=365, value=30)

                st.markdown("**Location**")
                col3, col4 = st.columns(2)
                with col3:
                    address = st.text_area("Address*")
                    city = st.text_input("City*")

                with col4:
                    state_province = st.text_input("State/Province")
                    country = st.text_input("Country*")
                    postal_code = st.text_input("Postal Code")

                description = st.text_area("Property Description*", height=100)

                st.markdown("**Amenities**")
                amenities = st.multiselect("Select all amenities available:", [
                    "WiFi", "Kitchen", "Washing machine", "Dryer", "Air conditioning", "Heating",
                    "Pool", "Hot tub", "Gym", "Parking", "Pet-friendly", "Smoking allowed",
                    "Wheelchair accessible", "Laptop-friendly workspace", "TV", "Fireplace",
                    "Balcony", "Garden", "BBQ grill", "Beach access", "Ski access"
                ])

                st.markdown("**House Rules**")
                house_rules = st.text_area("House Rules", placeholder="e.g., No smoking, No parties, Check-in after 3 PM")

                st.markdown("**Cancellation Policy**")
                cancellation_policy = st.selectbox("Cancellation Policy", [
                    "Flexible", "Moderate", "Strict", "Super Strict"
                ])

                # Photo upload (mock)
                st.markdown("**Photos**")
                uploaded_files = st.file_uploader("Upload property photos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

                submitted = st.form_submit_button("Add Property", use_container_width=True)

                if submitted:
                    if not all([property_title, property_type, address, city, country, description]):
                        st.error("Please fill in all required fields marked with *")
                    else:
                        new_property = {
                            'id': len(st.session_state.host_properties) + 1,
                            'title': property_title,
                            'type': property_type,
                            'max_guests': max_guests,
                            'bedrooms': bedrooms,
                            'bathrooms': bathrooms,
                            'price_per_night': price_per_night,
                            'cleaning_fee': cleaning_fee,
                            'security_deposit': security_deposit,
                            'minimum_stay': minimum_stay,
                            'maximum_stay': maximum_stay,
                            'address': address,
                            'city': city,
                            'state_province': state_province,
                            'country': country,
                            'postal_code': postal_code,
                            'description': description,
                            'amenities': amenities,
                            'house_rules': house_rules,
                            'cancellation_policy': cancellation_policy,
                            'photos': len(uploaded_files) if uploaded_files else 0,
                            'status': 'Active',
                            'created_date': date.today()
                        }

                        st.session_state.host_properties.append(new_property)
                        st.success(f"Property '{property_title}' added successfully!")
                        st.rerun()

        with tab2:
            st.markdown("### My Properties")

            if not st.session_state.host_properties:
                st.info("You haven't added any properties yet. Use the 'Add Property' tab to get started!")
            else:
                for prop in st.session_state.host_properties:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 1])

                        with col1:
                            st.markdown(f"**{prop['title']}**")
                            st.write(f"📍 {prop['city']}, {prop['country']}")
                            st.write(f"🏠 {prop['type']} • 👥 {prop['max_guests']} guests")

                        with col2:
                            st.write(f"💰 ${prop['price_per_night']}/night")
                            st.write(f"📅 Added: {prop['created_date']}")
                            status_color = "🟢" if prop['status'] == 'Active' else "🔴"
                            st.write(f"{status_color} {prop['status']}")

                        with col3:
                            if st.button("Edit", key=f"edit_{prop['id']}", use_container_width=True):
                                st.info("Edit functionality would be implemented here")
                            if st.button("Delete", key=f"delete_{prop['id']}", use_container_width=True):
                                st.session_state.host_properties = [p for p in st.session_state.host_properties if p['id'] != prop['id']]
                                st.rerun()

                        st.markdown("---")

        with tab3:
            st.markdown("### Analytics Dashboard")

            if st.session_state.host_properties:
                # Mock analytics data
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Properties", len(st.session_state.host_properties))

                with col2:
                    avg_price = sum(p['price_per_night'] for p in st.session_state.host_properties) / len(st.session_state.host_properties)
                    st.metric("Avg. Price/Night", f"${avg_price:.0f}")

                with col3:
                    st.metric("Total Bookings", "23", "↗️ +5")

                with col4:
                    st.metric("Revenue (Month)", "$2,450", "↗️ +12%")

                # Mock chart
                chart_data = pd.DataFrame({
                    'Date': pd.date_range('2024-01-01', periods=30),
                    'Bookings': [1, 0, 2, 1, 0, 3, 2, 1, 0, 1, 2, 0, 1, 3, 2, 1, 0, 2, 1, 0, 3, 1, 2, 0, 1, 2, 3, 1, 0, 2]
                })

                st.markdown("### Booking Trends")
                st.line_chart(chart_data.set_index('Date'))
            else:
                st.info("Add properties to see analytics data!")

    def run(self):
        """Main application runner"""
        # Check if user wants to access host interface
        if st.session_state.is_host:
            st.sidebar.markdown("## 🏠 Host Menu")
            if st.sidebar.button("Host Dashboard", use_container_width=True):
                st.session_state.current_step = 'host'
                st.rerun()
            st.sidebar.markdown("---")

        # Progress indicator for travel planning
        if st.session_state.current_step not in ['landing', 'preferences', 'host']:
            progress_steps = ['step1', 'step2', 'step3', 'step4', 'step5', 'step6', 'step7']
            current_index = progress_steps.index(st.session_state.current_step) if st.session_state.current_step in progress_steps else 0
            progress = (current_index + 1) / len(progress_steps)

            st.progress(progress)
            st.markdown(f"**Step {current_index + 1} of {len(progress_steps)}**")
            st.markdown("---")

        # Route to appropriate page based on current step
        if not st.session_state.user_registered:
            self.render_landing_page()
        elif st.session_state.current_step == 'preferences':
            self.render_preferences_page()
        elif st.session_state.current_step == 'step1':
            self.render_step1_travel_wishes()
        elif st.session_state.current_step == 'step2':
            self.render_step2_destination()
        elif st.session_state.current_step == 'step3':
            self.render_step3_transportation()
        elif st.session_state.current_step == 'step4':
            self.render_step4_accommodation()
        elif st.session_state.current_step == 'step5':
            self.render_step5_cuisine()
        elif st.session_state.current_step == 'step6':
            self.render_step6_experiences()
        elif st.session_state.current_step == 'step7':
            self.render_step7_itinerary()
        elif st.session_state.current_step == 'host':
            self.render_host_interface()
        else:
            st.error(f"Unknown step: {st.session_state.current_step}")

    def render_step5_cuisine(self):
        """Step 5: Cuisine and restaurant options"""
        st.markdown("## 🍽️ Step 5: Cuisine Options")
        st.markdown("Discover amazing dining experiences at your destination!")

        destination = st.session_state.selected_destination.get('name', 'your destination')
        st.markdown(f"**Dining options in {destination}**")

        # Dietary preferences
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🥗 Dietary Preferences")
            dietary_prefs = st.multiselect("Select your dietary preferences:", [
                "No restrictions", "Vegetarian", "Vegan", "Gluten-free", "Halal",
                "Kosher", "Dairy-free", "Nut allergies", "Seafood allergy"
            ])

            cuisine_types = st.multiselect("Preferred cuisine types:", [
                "Local/Traditional", "Italian", "French", "Asian", "Mexican",
                "Mediterranean", "Indian", "Japanese", "Thai", "American"
            ])

        with col2:
            st.markdown("### 💰 Budget & Style")
            dining_budget = st.selectbox("Dining budget per meal:", [
                "Budget ($10-25)", "Mid-range ($25-60)", "Fine dining ($60-150)", "Luxury ($150+)"
            ])

            dining_style = st.multiselect("Dining experiences you want:", [
                "Street food", "Casual dining", "Fine dining", "Rooftop restaurants",
                "Local markets", "Food tours", "Cooking classes", "Wine tasting"
            ])

        # Mock restaurant recommendations
        st.markdown("### 🍴 Recommended Restaurants")

        restaurants = [
            {"name": "Le Petit Bistro", "cuisine": "French", "price": "$$$$", "rating": 4.8, "specialty": "Classic French cuisine with modern twist"},
            {"name": "Sakura Sushi", "cuisine": "Japanese", "price": "$$$", "rating": 4.7, "specialty": "Fresh sushi and traditional Japanese dishes"},
            {"name": "Street Food Market", "cuisine": "Local", "price": "$", "rating": 4.5, "specialty": "Authentic local street food experience"},
            {"name": "Rooftop Garden", "cuisine": "Mediterranean", "price": "$$$", "rating": 4.6, "specialty": "Mediterranean cuisine with city views"}
        ]

        selected_restaurants = []

        for i, restaurant in enumerate(restaurants):
            col_a, col_b, col_c = st.columns([2, 2, 1])

            with col_a:
                st.markdown(f"**{restaurant['name']}**")
                st.write(f"🍽️ {restaurant['cuisine']} • {restaurant['price']} • ⭐ {restaurant['rating']}")

            with col_b:
                st.write(restaurant['specialty'])

            with col_c:
                if st.checkbox("Add to itinerary", key=f"restaurant_{i}"):
                    selected_restaurants.append(restaurant)

        st.markdown("---")

        # Show different buttons based on login status
        if st.session_state.get('user_registered', False) and st.session_state.get('user_id', None):
            # Logged in users get the complete trip planning button
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("← Back to Accommodation", use_container_width=True):
                    st.session_state.current_step = 'step4'
                    st.rerun()

            with col2:
                if st.button("🎉 Complete Trip Planning", use_container_width=True, key="complete_trip_step5"):
                    # Save restaurants and go directly to final itinerary
                    st.session_state.selected_restaurants = selected_restaurants

                    # Save travel plan to database
                    if st.session_state.user_id:
                        # Convert dates to strings for JSON serialization
                        travel_dates = st.session_state.travel_plans.get('travel_dates', {})
                        if isinstance(travel_dates, dict):
                            travel_dates_str = {}
                            for key, value in travel_dates.items():
                                if hasattr(value, 'strftime'):  # Check if it's a date object
                                    travel_dates_str[key] = value.strftime('%Y-%m-%d')
                                else:
                                    travel_dates_str[key] = str(value)
                        else:
                            travel_dates_str = str(travel_dates)

                        travel_plan = {
                            'destination': st.session_state.travel_plans.get('destination', 'Unknown'),
                            'travel_dates': travel_dates_str,
                            'accommodation': st.session_state.travel_plans.get('selected_accommodation', {}),
                            'transport': st.session_state.travel_plans.get('selected_transport', {}),
                            'restaurants': selected_restaurants,
                            'experiences': [],  # No experiences selected yet
                            'budget': st.session_state.travel_plans.get('budget', 0),
                            'travelers': st.session_state.travel_plans.get('travelers', 1),
                            'trip_type': st.session_state.travel_plans.get('trip_type', 'Leisure'),
                            'accommodation_preference': st.session_state.travel_plans.get('accommodation_preference', [])
                        }

                        self.db.save_travel_plan(
                            st.session_state.user_id,
                            f"Trip to {travel_plan['destination']}",
                            travel_plan['destination'],
                            travel_dates_str,
                            travel_plan
                        )

                    st.session_state.current_step = 'step7'
                    st.rerun()

            with col3:
                if st.button("Continue to Experiences →", use_container_width=True):
                    st.session_state.selected_restaurants = selected_restaurants
                    st.session_state.current_step = 'step6'
                    st.success(f"Added {len(selected_restaurants)} restaurants to your itinerary!")
                    st.rerun()
        else:
            # Non-logged in users get the regular flow
            col1, col2 = st.columns(2)

            with col1:
                if st.button("← Back to Accommodation", use_container_width=True):
                    st.session_state.current_step = 'step4'
                    st.rerun()

            with col2:
                if st.button("Continue to Experiences →", use_container_width=True):
                    st.session_state.selected_restaurants = selected_restaurants
                    st.session_state.current_step = 'step6'
                    st.success(f"Added {len(selected_restaurants)} restaurants to your itinerary!")
                    st.rerun()

            # Show login prompt and plan new trip option
            st.info("🔐 Sign in to save your trip and access booking features!")

            # Plan New Trip button for non-logged users too
            if st.button("🔄 Plan New Trip", use_container_width=True, key="plan_new_trip_step5"):
                # Reset all travel planning session state
                st.session_state.current_step = 'step1'
                st.session_state.travel_plans = {}
                st.session_state.selected_destination = {}
                st.session_state.selected_transport = {}
                st.session_state.selected_accommodation = {}
                st.session_state.selected_restaurants = []
                st.session_state.selected_experiences = []
                st.session_state.final_itinerary = {}

                # Reset swipe states
                if 'current_destination_index' in st.session_state:
                    del st.session_state.current_destination_index
                if 'liked_destinations' in st.session_state:
                    del st.session_state.liked_destinations
                if 'rejected_destinations' in st.session_state:
                    del st.session_state.rejected_destinations
                if 'current_accommodation_index' in st.session_state:
                    del st.session_state.current_accommodation_index
                if 'liked_accommodations' in st.session_state:
                    del st.session_state.liked_accommodations
                if 'rejected_accommodations' in st.session_state:
                    del st.session_state.rejected_accommodations

                st.success("Ready to plan your next adventure!")
                st.rerun()

    def render_step6_experiences(self):
        """Step 6: Experiences and activities"""
        st.markdown("## 🎯 Step 6: Experiences & Activities")
        st.markdown("Choose exciting activities and experiences for your trip!")

        destination = st.session_state.selected_destination.get('name', 'your destination')

        # Activity categories
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🎨 Activity Categories")
            activity_categories = st.multiselect("What interests you?", [
                "Cultural & Historical", "Adventure & Sports", "Nature & Wildlife",
                "Art & Museums", "Entertainment & Nightlife", "Shopping",
                "Wellness & Spa", "Food & Drink", "Photography", "Local Experiences"
            ])

        with col2:
            st.markdown("### ⏰ Time Preferences")
            time_preferences = st.multiselect("When do you prefer activities?", [
                "Morning (6AM-12PM)", "Afternoon (12PM-6PM)", "Evening (6PM-10PM)", "Night (10PM+)"
            ])

            activity_pace = st.selectbox("Activity pace:", [
                "Relaxed - 1-2 activities per day",
                "Moderate - 2-3 activities per day",
                "Active - 3+ activities per day"
            ])

        # Mock experiences
        st.markdown("### 🌟 Available Experiences")

        experiences = [
            {"name": "City Walking Tour", "category": "Cultural", "duration": "3 hours", "price": 25, "rating": 4.8, "description": "Explore historic landmarks with local guide"},
            {"name": "Cooking Class", "category": "Food & Drink", "duration": "4 hours", "price": 85, "rating": 4.9, "description": "Learn to cook traditional local dishes"},
            {"name": "Museum Pass", "category": "Art & Museums", "duration": "Full day", "price": 45, "rating": 4.7, "description": "Access to top 5 museums in the city"},
            {"name": "Sunset Boat Tour", "category": "Nature", "duration": "2 hours", "price": 65, "rating": 4.6, "description": "Scenic boat tour with stunning sunset views"},
            {"name": "Adventure Park", "category": "Adventure", "duration": "Half day", "price": 95, "rating": 4.5, "description": "Zip-lining and outdoor adventure activities"}
        ]

        selected_experiences = []

        for i, exp in enumerate(experiences):
            col_a, col_b, col_c = st.columns([2, 2, 1])

            with col_a:
                st.markdown(f"**{exp['name']}**")
                st.write(f"🏷️ {exp['category']} • ⏱️ {exp['duration']}")
                st.write(f"⭐ {exp['rating']} • 💰 ${exp['price']}")

            with col_b:
                st.write(exp['description'])

            with col_c:
                if st.checkbox("Add to trip", key=f"experience_{i}"):
                    selected_experiences.append(exp)

        st.markdown("---")

        # Show different buttons based on login status
        if st.session_state.get('user_registered', False) and st.session_state.get('user_id', None):
            # Logged in users get the complete trip planning button
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("← Back to Dining", use_container_width=True):
                    st.session_state.current_step = 'step5'
                    st.rerun()

            with col2:
                if st.button("🎉 Complete Trip Planning", use_container_width=True, key="complete_trip_step6"):
                    # Save experiences and go directly to final itinerary
                    st.session_state.selected_experiences = selected_experiences

                    # Save travel plan to database
                    if st.session_state.user_id:
                        # Convert dates to strings for JSON serialization
                        travel_dates = st.session_state.travel_plans.get('travel_dates', {})
                        if isinstance(travel_dates, dict):
                            travel_dates_str = {}
                            for key, value in travel_dates.items():
                                if hasattr(value, 'strftime'):  # Check if it's a date object
                                    travel_dates_str[key] = value.strftime('%Y-%m-%d')
                                else:
                                    travel_dates_str[key] = str(value)
                        else:
                            travel_dates_str = str(travel_dates)

                        travel_plan = {
                            'destination': st.session_state.travel_plans.get('destination', 'Unknown'),
                            'travel_dates': travel_dates_str,
                            'accommodation': st.session_state.travel_plans.get('selected_accommodation', {}),
                            'transport': st.session_state.travel_plans.get('selected_transport', {}),
                            'restaurants': st.session_state.get('selected_restaurants', []),
                            'experiences': selected_experiences,
                            'budget': st.session_state.travel_plans.get('budget', 0),
                            'travelers': st.session_state.travel_plans.get('travelers', 1),
                            'trip_type': st.session_state.travel_plans.get('trip_type', 'Leisure'),
                            'accommodation_preference': st.session_state.travel_plans.get('accommodation_preference', [])
                        }

                        self.db.save_travel_plan(
                            st.session_state.user_id,
                            f"Trip to {travel_plan['destination']}",
                            travel_plan['destination'],
                            travel_dates_str,
                            travel_plan
                        )

                    st.session_state.current_step = 'step7'
                    st.rerun()

            with col3:
                if st.button("Create My Itinerary →", use_container_width=True):
                    st.session_state.selected_experiences = selected_experiences
                    st.session_state.current_step = 'step7'
                    st.success(f"Added {len(selected_experiences)} experiences to your trip!")
                    st.rerun()
        else:
            # Non-logged in users get the regular flow
            col1, col2 = st.columns(2)

            with col1:
                if st.button("← Back to Dining", use_container_width=True):
                    st.session_state.current_step = 'step5'
                    st.rerun()

            with col2:
                if st.button("Create My Itinerary →", use_container_width=True):
                    st.session_state.selected_experiences = selected_experiences
                    st.session_state.current_step = 'step7'
                    st.success(f"Added {len(selected_experiences)} experiences to your trip!")
                    st.rerun()

            # Show login prompt and plan new trip option
            st.info("🔐 Sign in to save your trip and access booking features!")

            # Plan New Trip button for non-logged users too
            if st.button("🔄 Plan New Trip", use_container_width=True, key="plan_new_trip_step6"):
                # Reset all travel planning session state
                st.session_state.current_step = 'step1'
                st.session_state.travel_plans = {}
                st.session_state.selected_destination = {}
                st.session_state.selected_transport = {}
                st.session_state.selected_accommodation = {}
                st.session_state.selected_restaurants = []
                st.session_state.selected_experiences = []
                st.session_state.final_itinerary = {}

                # Reset swipe states
                if 'current_destination_index' in st.session_state:
                    del st.session_state.current_destination_index
                if 'liked_destinations' in st.session_state:
                    del st.session_state.liked_destinations
                if 'rejected_destinations' in st.session_state:
                    del st.session_state.rejected_destinations
                if 'current_accommodation_index' in st.session_state:
                    del st.session_state.current_accommodation_index
                if 'liked_accommodations' in st.session_state:
                    del st.session_state.liked_accommodations
                if 'rejected_accommodations' in st.session_state:
                    del st.session_state.rejected_accommodations

                st.success("Ready to plan your next adventure!")
                st.rerun()

    def render_step7_itinerary(self):
        """Step 7: Final itinerary generation and selection"""
        st.markdown("## 📋 Step 7: Your Complete Travel Itinerary")
        st.markdown("Review and customize your perfect trip!")

        # Trip summary
        destination = st.session_state.selected_destination.get('name', 'Unknown')
        accommodation = st.session_state.selected_accommodation.get('title', 'Not selected')
        transport = st.session_state.selected_transport.get('flight', {}).get('airline', 'Not selected')

        st.markdown("### 📊 Trip Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info(f"""
            **🗺️ Destination**
            {destination}

            **📅 Duration**
            {st.session_state.selected_destination.get('duration', 'Not specified')}
            """)

        with col2:
            st.info(f"""
            **🚗 Transportation**
            Ground transport selected

            **🏠 Accommodation**
            {accommodation}
            """)

        with col3:
            restaurants_count = len(st.session_state.selected_restaurants)
            experiences_count = len(st.session_state.selected_experiences)

            st.info(f"""
            **🍽️ Restaurants**
            {restaurants_count} selected

            **🎯 Experiences**
            {experiences_count} selected
            """)

        # Detailed itinerary
        st.markdown("### 📅 Day-by-Day Itinerary")

        # Mock itinerary generation
        days = ["Day 1", "Day 2", "Day 3"]

        # Get selected restaurants and experiences
        selected_restaurants = st.session_state.get('selected_restaurants', [])
        selected_experiences = st.session_state.get('selected_experiences', [])

        # COMMENTED OUT - Flight information
        # flight_info = st.session_state.get('selected_transport', {}).get('flight', {})
        # arrival_time = flight_info.get('arrival', '2:30 PM')
        # departure_time = flight_info.get('departure', '8:00 AM')

        # Default arrival/departure times for itinerary planning
        arrival_time = '2:30 PM'
        departure_time = '6:00 PM'

        for day in days:
            with st.expander(f"📆 {day}", expanded=True):
                if day == "Day 1":
                    lunch_restaurant = selected_restaurants[0]['name'] if len(selected_restaurants) > 0 else "local restaurant"
                    dinner_restaurant = selected_restaurants[1]['name'] if len(selected_restaurants) > 1 else "recommended restaurant"

                    # Calculate arrival time and subsequent activities
                    arrival_hour = int(arrival_time.split(':')[0]) if ':' in arrival_time else 14
                    if 'PM' in arrival_time and arrival_hour != 12:
                        arrival_hour += 12
                    elif 'AM' in arrival_time and arrival_hour == 12:
                        arrival_hour = 0

                    checkin_hour = arrival_hour + 1
                    lunch_hour = max(checkin_hour + 1, 14)  # Ensure lunch is at least 2 PM

                    st.markdown(f"""
                    **Morning/Afternoon ({arrival_time})**
                    - 🚗 Arrive at destination
                    - 🏠 Check-in and settle in ({checkin_hour}:00)

                    **Afternoon ({lunch_hour}:00)**
                    - 🍽️ Lunch at {lunch_restaurant}
                    - 🚶 City walking tour

                    **Evening (7:00 PM)**
                    - 🍽️ Dinner at {dinner_restaurant}
                    - 🌙 Evening stroll around neighborhood
                    """)
                elif day == "Day 2":
                    lunch_restaurant = selected_restaurants[2]['name'] if len(selected_restaurants) > 2 else "local café"
                    dinner_restaurant = selected_restaurants[3]['name'] if len(selected_restaurants) > 3 else "restaurant with a view"
                    experience_1 = selected_experiences[0]['name'] if len(selected_experiences) > 0 else "Museum visit"
                    experience_2 = selected_experiences[1]['name'] if len(selected_experiences) > 1 else "Adventure activity"

                    st.markdown(f"""
                    **Morning (9:00 AM)**
                    - 🍳 Breakfast at accommodation
                    - 🎨 {experience_1}

                    **Afternoon (1:00 PM)**
                    - 🍽️ Lunch at {lunch_restaurant}
                    - 🎯 {experience_2}

                    **Evening (6:00 PM)**
                    - 🌅 Sunset boat tour
                    - 🍽️ Dinner at {dinner_restaurant}
                    """)
                else:
                    final_restaurant = selected_restaurants[4]['name'] if len(selected_restaurants) > 4 else selected_restaurants[0]['name'] if len(selected_restaurants) > 0 else "favorite spot"
                    final_experience = selected_experiences[2]['name'] if len(selected_experiences) > 2 else "Shopping and souvenirs"

                    # Calculate departure timing
                    departure_hour = int(departure_time.split(':')[0]) if ':' in departure_time else 18
                    if 'PM' in departure_time and departure_hour != 12:
                        departure_hour += 12
                    elif 'AM' in departure_time and departure_hour == 12:
                        departure_hour = 0

                    airport_transfer_hour = max(departure_hour - 2, 16)  # 2 hours before flight, minimum 4 PM
                    checkout_hour = max(airport_transfer_hour - 1, 14)  # 1 hour before transfer, minimum 2 PM

                    st.markdown(f"""
                    **Morning (10:00 AM)**
                    - 🍳 Leisurely breakfast
                    - 🛍️ {final_experience}

                    **Afternoon ({checkout_hour}:00)**
                    - 🍽️ Final meal at {final_restaurant}
                    - 📦 Pack and check out

                    **Evening ({airport_transfer_hour}:00)**
                    - 🚗 Departure preparation
                    - 🚗 Leave destination at {departure_time}
                    """)

        # Budget breakdown
        st.markdown("### 💰 Estimated Budget Breakdown")

        # Mock budget calculation
        # flight_cost = 450  # COMMENTED OUT - Flight costs
        accommodation_cost = 85 * 3  # 3 nights
        restaurant_cost = len(st.session_state.selected_restaurants) * 50
        experience_cost = sum(exp.get('price', 0) for exp in st.session_state.selected_experiences)
        transport_cost = 100

        total_cost = accommodation_cost + restaurant_cost + experience_cost + transport_cost

        budget_data = {
            'Category': ['Accommodation', 'Dining', 'Experiences', 'Local Transport'],
            'Cost': [accommodation_cost, restaurant_cost, experience_cost, transport_cost]
        }

        budget_df = pd.DataFrame(budget_data)

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = px.pie(budget_df, values='Cost', names='Category', title='Budget Breakdown')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"### Total Trip Cost")
            st.markdown(f"## ${total_cost:,}")

            for _, row in budget_df.iterrows():
                st.write(f"**{row['Category']}:** ${row['Cost']:,}")

        # Action buttons - only show if user is logged in
        if st.session_state.get('user_registered', False) and st.session_state.get('user_id', None):
            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col2:
                if st.button("📧 Email Itinerary", use_container_width=True):
                    st.success("Itinerary sent to your email!")
                if st.button("💳 Book This Trip", use_container_width=True):
                    st.success("🎉 Trip booked successfully! Have an amazing journey!")

                # Plan Another Trip button (separate from booking)
                if st.button("🔄 Plan Another Trip", use_container_width=True):
                    # Reset all travel planning session state
                    st.session_state.current_step = 'step1'
                    st.session_state.travel_plans = {}
                    st.session_state.selected_destination = {}
                    st.session_state.selected_transport = {}
                    st.session_state.selected_accommodation = {}
                    st.session_state.selected_restaurants = []
                    st.session_state.selected_experiences = []
                    st.session_state.final_itinerary = {}

                    # Reset swipe states
                    if 'current_destination_index' in st.session_state:
                        del st.session_state.current_destination_index
                    if 'liked_destinations' in st.session_state:
                        del st.session_state.liked_destinations
                    if 'rejected_destinations' in st.session_state:
                        del st.session_state.rejected_destinations
                    if 'current_accommodation_index' in st.session_state:
                        del st.session_state.current_accommodation_index
                    if 'liked_accommodations' in st.session_state:
                        del st.session_state.liked_accommodations
                    if 'rejected_accommodations' in st.session_state:
                        del st.session_state.rejected_accommodations

                    st.success("Ready to plan your next adventure!")
                    st.rerun()
        else:
            # Show message for non-logged in users
            st.markdown("---")
            st.info("🔐 Please sign in to save your trip and access booking features.")

# Run the application
if __name__ == "__main__":
    app = TravelEaseApp()
    app.run()
