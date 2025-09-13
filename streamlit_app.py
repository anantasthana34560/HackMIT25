import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io

# Configure Streamlit page
st.set_page_config(
    page_title="TravelEase - Your AI Travel Companion",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

class TravelEaseApp:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        """Initialize session state variables"""
        # User account and profile
        if 'user_registered' not in st.session_state:
            st.session_state.user_registered = False
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
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #1E88E5; font-size: 3.5rem; margin-bottom: 1rem;'>🌍 TravelEase</h1>
            <h2 style='color: #424242; font-weight: 300; margin-bottom: 2rem;'>Your AI-Powered Travel Companion</h2>
            <p style='font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto;'>
                Plan everything from flights to accommodations, restaurants to experiences - all in one place!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🚀 Create Your Account")

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
                        # Save user profile
                        st.session_state.user_profile = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
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

                        if "Host" in account_type:
                            st.session_state.is_host = True

                        st.session_state.user_registered = True
                        st.session_state.current_step = 'preferences'
                        st.success("Account created successfully! Let's learn more about your travel preferences.")
                        st.rerun()

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
                    "Hotels", "Vacation rentals/Airbnb", "Hostels", "Resorts",
                    "Boutique hotels", "Camping", "Luxury accommodations"
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
                st.session_state.user_preferences = {
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

                st.session_state.current_step = 'step1'
                st.success("Preferences saved! Let's start planning your perfect trip.")
                st.rerun()

    def render_step1_travel_wishes(self):
        """Step 1: Travel wishes and plans"""
        st.markdown("## 🎯 Step 1: Tell Us About Your Dream Trip")
        st.markdown("Share your travel wishes and we'll help make them come true!")

        with st.form("travel_wishes"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Trip Details**")
                destination_input = st.text_input(
                    "Where would you like to go? (City, Country, or 'Surprise me!')",
                    placeholder="e.g., Paris, France or Southeast Asia"
                )

                trip_duration = st.selectbox("How long is your trip?", [
                    "Weekend (2-3 days)", "Short trip (4-7 days)",
                    "Week-long (8-14 days)", "Extended (2-4 weeks)", "Month or longer"
                ])

                travel_dates = st.date_input(
                    "Preferred travel dates",
                    value=[date.today(), date.today()],
                    help="Select start and end dates, or approximate timeframe"
                )

                flexibility = st.selectbox("How flexible are your dates?", [
                    "Exact dates only", "Within a week", "Within a month",
                    "Flexible - best prices", "Seasonal preference"
                ])

            with col2:
                st.markdown("**Travel Companions**")
                travel_group = st.selectbox("Who's traveling with you?", [
                    "Just me (solo)", "Me + 1 person", "Small group (3-4 people)",
                    "Large group (5+ people)", "Family with children", "Business trip"
                ])

                if travel_group != "Just me (solo)":
                    group_details = st.text_area(
                        "Tell us about your travel companions",
                        placeholder="Ages, relationships, special needs, etc."
                    )
                else:
                    group_details = ""

                budget_total = st.selectbox("Total budget for this trip", [
                    "Under $1,000", "$1,000 - $3,000", "$3,000 - $5,000",
                    "$5,000 - $10,000", "$10,000 - $20,000", "$20,000+", "No budget limit"
                ])

            st.markdown("**Trip Preferences**")
            col3, col4 = st.columns(2)

            with col3:
                trip_style = st.multiselect("What kind of vacation do you want?", [
                    "Relaxing/Peaceful", "Adventure/Active", "Cultural immersion",
                    "Party/Nightlife", "Romantic getaway", "Family fun",
                    "Business + leisure", "Wellness/Spa", "Food & wine focused"
                ])

                must_have_activities = st.multiselect("Must-have activities", [
                    "Beach time", "Mountain hiking", "City exploration", "Museums/Art",
                    "Local cuisine", "Shopping", "Nightlife", "Photography",
                    "Water sports", "Cultural sites", "Nature/Wildlife", "Adventure sports"
                ])

            with col4:
                accommodation_preference = st.selectbox("Accommodation preference for this trip", [
                    "Budget-friendly", "Mid-range comfort", "Luxury experience",
                    "Unique/Local experience", "Family-friendly", "Romantic setting"
                ])

                special_occasions = st.multiselect("Any special occasions?", [
                    "None", "Birthday", "Anniversary", "Honeymoon", "Graduation",
                    "Retirement", "Holiday celebration", "Business milestone"
                ])

            additional_wishes = st.text_area(
                "Any other experiences, wishes, or requirements?",
                placeholder="Tell us anything else that would make this trip perfect for you..."
            )

            submitted = st.form_submit_button("Continue to Destination Selection", use_container_width=True)

            if submitted:
                if not destination_input:
                    st.error("Please tell us where you'd like to go!")
                else:
                    st.session_state.travel_plans = {
                        'destination_input': destination_input,
                        'trip_duration': trip_duration,
                        'travel_dates': travel_dates,
                        'flexibility': flexibility,
                        'travel_group': travel_group,
                        'group_details': group_details,
                        'budget_total': budget_total,
                        'trip_style': trip_style,
                        'must_have_activities': must_have_activities,
                        'accommodation_preference': accommodation_preference,
                        'special_occasions': special_occasions,
                        'additional_wishes': additional_wishes
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
                            {"name": "Paris, France", "description": "City of Light with world-class museums, cuisine, and romance", "best_time": "April-June, September-October", "avg_temp": "15-25°C"},
                            {"name": "Nice, France", "description": "French Riviera with stunning beaches and Mediterranean charm", "best_time": "May-September", "avg_temp": "18-28°C"},
                            {"name": "Lyon, France", "description": "Gastronomic capital with Renaissance architecture", "best_time": "April-October", "avg_temp": "12-26°C"}
                        ]
                    elif 'italy' in destination_input.lower():
                        suggested_destinations = [
                            {"name": "Rome, Italy", "description": "Eternal City with ancient history and incredible cuisine", "best_time": "April-June, September-October", "avg_temp": "15-25°C"},
                            {"name": "Florence, Italy", "description": "Renaissance art and architecture in Tuscany", "best_time": "April-June, September-October", "avg_temp": "15-25°C"},
                            {"name": "Venice, Italy", "description": "Romantic canals and unique island city", "best_time": "April-June, September-October", "avg_temp": "15-25°C"}
                        ]
                    elif 'india' in destination_input.lower():
                        suggested_destinations = [
                            {"name": "Mumbai, India", "description": "Financial capital with Bollywood glamour and incredible street food", "best_time": "November-March", "avg_temp": "20-32°C"},
                            {"name": "Delhi, India", "description": "Historic capital with Mughal architecture and vibrant markets", "best_time": "October-March", "avg_temp": "15-30°C"},
                            {"name": "Goa, India", "description": "Tropical paradise with pristine beaches and Portuguese heritage", "best_time": "November-February", "avg_temp": "23-32°C"}
                        ]
                    else:
                        # Generic popular destinations
                        suggested_destinations = [
                            {"name": "Paris, France", "description": "City of Light with world-class museums, cuisine, and romance", "best_time": "April-June, September-October", "avg_temp": "15-25°C"},
                            {"name": "Tokyo, Japan", "description": "Modern metropolis blending tradition with cutting-edge technology", "best_time": "March-May, September-November", "avg_temp": "10-26°C"},
                            {"name": "New York City, USA", "description": "The city that never sleeps with iconic landmarks", "best_time": "April-June, September-November", "avg_temp": "10-25°C"}
                        ]

            selected_dest = st.radio(
                f"Based on your interest in '{destination_input}', here are our top recommendations:",
                options=[dest["name"] for dest in suggested_destinations],
                format_func=lambda x: f"📍 {x}"
            )

            # Show details of selected destination
            selected_dest_info = next(dest for dest in suggested_destinations if dest["name"] == selected_dest)

            st.info(f"""
            **{selected_dest_info['name']}**

            {selected_dest_info['description']}

            🌡️ **Average Temperature:** {selected_dest_info['avg_temp']}
            📅 **Best Time to Visit:** {selected_dest_info['best_time']}
            """)

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
            if st.button("Continue to Transportation →", use_container_width=True):
                st.session_state.selected_destination = {
                    'name': selected_dest,
                    'info': selected_dest_info,
                    'dates': new_dates if modify_dates else travel_dates,
                    'duration': new_duration if modify_dates else trip_duration
                }
                st.session_state.current_step = 'step3'
                st.success(f"Destination set: {selected_dest}")
                st.rerun()

    def render_step3_transportation(self):
        """Step 3: Transportation/How to get there"""
        st.markdown("## ✈️ Step 3: How to Get There")
        st.markdown("Let's find the best way to reach your destination!")

        destination = st.session_state.selected_destination.get('name', 'your destination')
        user_location = f"{st.session_state.user_profile.get('city', '')}, {st.session_state.user_profile.get('country', '')}"

        st.markdown(f"**From:** {user_location}")
        st.markdown(f"**To:** {destination}")

        tab1, tab2, tab3 = st.tabs(["✈️ Flights", "🚗 Ground Transport", "🚢 Other Options"])

        with tab1:
            st.markdown("### Flight Options")

            # Mock flight data
            flights = [
                {"airline": "Delta Airlines", "departure": "8:00 AM", "arrival": "2:30 PM", "duration": "6h 30m", "stops": "Direct", "price": "$450", "class": "Economy"},
                {"airline": "United Airlines", "departure": "11:15 AM", "arrival": "6:45 PM", "duration": "7h 30m", "stops": "1 stop", "price": "$380", "class": "Economy"},
                {"airline": "Air France", "departure": "6:30 PM", "arrival": "11:00 AM+1", "duration": "8h 30m", "stops": "Direct", "price": "$650", "class": "Business"}
            ]

            selected_flight = st.radio("Choose your flight:", options=range(len(flights)), format_func=lambda i: f"{flights[i]['airline']} - {flights[i]['departure']} to {flights[i]['arrival']} ({flights[i]['duration']}) - {flights[i]['price']}")

            flight_details = flights[selected_flight]
            st.info(f"""
            **Selected Flight Details:**
            - **Airline:** {flight_details['airline']}
            - **Departure:** {flight_details['departure']}
            - **Arrival:** {flight_details['arrival']}
            - **Duration:** {flight_details['duration']}
            - **Stops:** {flight_details['stops']}
            - **Class:** {flight_details['class']}
            - **Price:** {flight_details['price']}
            """)

        with tab2:
            st.markdown("### Ground Transportation at Destination")

            transport_options = st.multiselect("Select transportation methods you'd like to use:", [
                "Airport shuttle", "Taxi/Uber", "Public transportation", "Rental car",
                "Hotel transfer", "Private driver", "Walking", "Bicycle rental"
            ])

            if "Rental car" in transport_options:
                car_type = st.selectbox("Preferred car type:", ["Economy", "Compact", "Mid-size", "Full-size", "SUV", "Luxury"])
                st.write(f"Car rental estimate: $35-85/day for {car_type}")

        with tab3:
            st.markdown("### Alternative Transportation")

            other_options = st.multiselect("Other transportation options:", [
                "Train", "Bus", "Ferry", "Cruise", "Private jet", "Road trip"
            ])

            if other_options:
                st.write("We'll research these options and include them in your itinerary!")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back to Destination", use_container_width=True):
                st.session_state.current_step = 'step2'
                st.rerun()

        with col2:
            if st.button("Continue to Accommodation →", use_container_width=True):
                st.session_state.selected_transport = {
                    'flight': flights[selected_flight],
                    'ground_transport': transport_options,
                    'other_options': other_options
                }
                st.session_state.current_step = 'step4'
                st.success("Transportation options saved!")
                st.rerun()

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

        # Mock property listings
        st.markdown("### 🏡 Available Properties")

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
                "superhost": True
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
                "superhost": True
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
                "superhost": False
            }
        ]

        for i, prop in enumerate(properties):
            with st.container():
                col_a, col_b, col_c = st.columns([2, 2, 1])

                with col_a:
                    st.markdown(f"**{prop['title']}**")
                    st.write(f"🏠 {prop['type']} • 👥 {prop['guests']} guests • 🛏️ {prop['bedrooms']} bedrooms")
                    st.write(f"⭐ {prop['rating']} ({prop['reviews']} reviews)")
                    if prop['superhost']:
                        st.markdown("🏆 **Superhost**")

                with col_b:
                    st.write(prop['description'])
                    st.write(f"**Host:** {prop['host']}")
                    amenities_text = ", ".join(prop['amenities'][:4])
                    if len(prop['amenities']) > 4:
                        amenities_text += f" + {len(prop['amenities']) - 4} more"
                    st.write(f"**Amenities:** {amenities_text}")

                with col_c:
                    st.markdown(f"### ${prop['price']}")
                    st.write("per night")
                    if st.button(f"Select", key=f"select_prop_{i}", use_container_width=True):
                        st.session_state.selected_accommodation = prop
                        st.success(f"Selected: {prop['title']}")

                st.markdown("---")

        # Navigation buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back to Transportation", use_container_width=True):
                st.session_state.current_step = 'step3'
                st.rerun()

        with col2:
            if st.button("Continue to Dining →", use_container_width=True):
                if st.session_state.selected_accommodation:
                    st.session_state.current_step = 'step5'
                    st.rerun()
                else:
                    st.error("Please select an accommodation first!")

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
            **✈️ Flight**
            {transport}

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

        for day in days:
            with st.expander(f"📆 {day}", expanded=True):
                if day == "Day 1":
                    st.markdown("""
                    **Morning (9:00 AM)**
                    - ✈️ Arrive at destination
                    - 🚗 Airport transfer to accommodation
                    - 🏠 Check-in and settle in

                    **Afternoon (2:00 PM)**
                    - 🍽️ Lunch at local restaurant
                    - 🚶 City walking tour

                    **Evening (7:00 PM)**
                    - 🍽️ Dinner at recommended restaurant
                    - 🌙 Evening stroll around neighborhood
                    """)
                elif day == "Day 2":
                    st.markdown("""
                    **Morning (9:00 AM)**
                    - 🍳 Breakfast at accommodation
                    - 🎨 Museum visit

                    **Afternoon (1:00 PM)**
                    - 🍽️ Lunch break
                    - 🎯 Adventure activity

                    **Evening (6:00 PM)**
                    - 🌅 Sunset boat tour
                    - 🍽️ Dinner with a view
                    """)
                else:
                    st.markdown("""
                    **Morning (10:00 AM)**
                    - 🍳 Leisurely breakfast
                    - 🛍️ Shopping and souvenirs

                    **Afternoon (2:00 PM)**
                    - 🍽️ Final meal at favorite spot
                    - 📦 Pack and check out

                    **Evening (6:00 PM)**
                    - 🚗 Transfer to airport
                    - ✈️ Departure
                    """)

        # Budget breakdown
        st.markdown("### 💰 Estimated Budget Breakdown")

        # Mock budget calculation
        flight_cost = 450
        accommodation_cost = 85 * 3  # 3 nights
        restaurant_cost = len(st.session_state.selected_restaurants) * 50
        experience_cost = sum(exp.get('price', 0) for exp in st.session_state.selected_experiences)
        transport_cost = 100

        total_cost = flight_cost + accommodation_cost + restaurant_cost + experience_cost + transport_cost

        budget_data = {
            'Category': ['Flight', 'Accommodation', 'Dining', 'Experiences', 'Local Transport'],
            'Cost': [flight_cost, accommodation_cost, restaurant_cost, experience_cost, transport_cost]
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

        # Action buttons
        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("← Back to Experiences", use_container_width=True):
                st.session_state.current_step = 'step6'
                st.rerun()

        with col2:
            if st.button("📧 Email Itinerary", use_container_width=True):
                st.success("Itinerary sent to your email!")

        with col3:
            if st.button("💳 Book This Trip", use_container_width=True):
                st.success("🎉 Trip booked successfully! Have an amazing journey!")
                # Reset for new trip
                if st.button("Plan Another Trip"):
                    st.session_state.current_step = 'step1'
                    st.rerun()

# Run the application
if __name__ == "__main__":
    app = TravelEaseApp()
    app.run()
