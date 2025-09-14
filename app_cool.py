# 1. Preference: what type of housing - deetya
# 2. Input travel plans: what dates, what location - deetya
# 3. Agent to propose staying options - yuga's api 
# 4. Presenting each option one by one and peope can swipe left or right 
# 5. Agent that uses swipes to create a stay per day  

from housing_listings import housing_listings
from cuisine_listings import cuisine_listings
from experience_listings import experience_listings

# --- Housing Filter ---
def filter_housing(user_preferences, travel_info):
    options = []
    for house in housing_listings:
        if house["location"] != travel_info["location"]:
            continue
        if user_preferences.get("safety_level") and house["safety"] != user_preferences["safety_level"]:
            continue
        if house["housing_type"] not in user_preferences.get("housing_type", []):
            continue
        if not (user_preferences["price_range"][0] <= house["cost_per_night"] <= user_preferences["price_range"][1]):
            continue
        if not any(a in house["amenities"] for a in travel_info.get("desired_amenities", [])):
            continue
        if not all(date in house["scheduled_dates"] for date in travel_info.get("dates", [])):
            continue
        options.append(house)
    return options

# --- Cuisine Filter ---
def filter_cuisine(user_preferences, travel_info):
    options = []
    for cuisine in cuisine_listings:
        if cuisine["location"] != travel_info["location"]:
            continue
        if cuisine["cuisine_type"] not in travel_info.get("cuisine_preferences", []):
            continue
        options.append(cuisine)
    return options

# --- Experience Filter ---
def filter_experiences(user_preferences, travel_info):
    options = []
    for exp in experience_listings:
        if exp["location"] != travel_info["location"]:
            continue
        if exp["experience"] not in travel_info.get("experience_preferences", []):
            continue
        options.append(exp)
    return options

# --- Agno Agent with Claude ---
from agno.agent import Agent
from agno.models.anthropic import Claude
import os 

def ai_travel_agent_agno(user_message, user_preferences, travel_info):
    housing_options = filter_housing(user_preferences, travel_info)
    cuisine_options = filter_cuisine(user_preferences, travel_info)
    experience_options = filter_experiences(user_preferences, travel_info)

    context = f"""
User Preferences: {user_preferences}\nTravel Info: {travel_info}\n\nHousing Options: {housing_options}\nCuisine Options: {cuisine_options}\nExperience Options: {experience_options}\n"""

    prompt = (
        "You are a helpful travel agent AI. Use the provided options and preferences to make recommendations.\n"
        f"{user_message}\n{context}"
    )

    agent = Agent(model=Claude(id="claude-opus-4-1-20250805"))
    agent.print_response(prompt)

# --- Example Usage ---
if __name__ == "__main__":
    from preferences import user_preferences
    from travel_info import travel_info
    user_message = "Plan my trip!"
    ai_travel_agent_agno(user_message, user_preferences, travel_info)


def get_recommendations(city, start_date, end_date, user_profile):
    # Filter by city and available dates
    houses = House.query.filter_by(city=city)
    houses = [h for h in houses if h.is_available(start_date, end_date)]
    # Filter by safety
    houses = [h for h in houses if h.safety_score > 7]
    # Rank by amenities matching user_profile
    houses = rank_by_amenities(houses, user_profile)
    return houses


def update_user_profile(user_profile, house, liked):
    if liked:
        for amenity in house.amenities:
            user_profile['amenities'][amenity] += 1
    else:
        for amenity in house.amenities:
            user_profile['amenities'][amenity] -= 1
    # Save user_profile to DB

