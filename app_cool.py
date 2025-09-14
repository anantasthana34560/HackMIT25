# 1. Preference: what type of housing - deetya
# 2. Input travel plans: what dates, what location - deetya
# 3. Agent to propose staying options - yuga's api 
# 4. Presenting each option one by one and peope can swipe left or right 
# 5. Agent that uses swipes to create a stay per day  

from housing_listings import housing_listings, housing_id_dict
from cuisine_listings import cuisine_listings, cuisine_id_dict
from experience_listings import experience_listings, experience_id_dict
from pydantic import BaseModel
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any
import json
import os

# ===== Schema =====
class ListOut(BaseModel):
    housing_ids: List[str]
    cuisine_ids: List[str]
    experience_ids: List[str]

# ===== Filters (fixed signatures & scoping) =====
def filter_cuisine(user_preferences: Dict[str, Any], travel_info: Dict[str, Any]):
    location = travel_info["location"]
    cuisine_type = user_preferences["cuisine_types"]
    return [c for c in cuisine_listings if c.get("location") == location and (c.get("cuisine_type") in cuisine_type or cuisine_type == [])]

def filter_experiences(user_preferences: Dict[str, Any], travel_info: Dict[str, Any]):
    location = travel_info["location"]
    experience_type = user_preferences["experience_types"]
    return [e for e in experience_listings if e.get("location") == location and (e.get("experience_type") in experience_type or experience_type == [])]

def filter_housing(user_preferences: Dict[str, Any], travel_info: Dict[str, Any]):
    location = travel_info["location"]
    dates = travel_info.get("dates", [])
    # require all requested dates to be in scheduled_dates
    out = []
    for h in housing_listings:
        if h.get("location") != location:
            continue
        # if dates and not all(d in h.get("scheduled_dates", []) for d in dates):
        #     continue
        out.append(h)
    return out

# ===== Agno Agent (Claude) =====
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools import tool

housing_agent = []
cuisine_agent = []
experience_agent = []

@tool(show_result=True)
def view_housing_option(housing_id : str) -> dict:
    return housing_id_dict[housing_id]

@tool(show_result=True)
def view_cuisine_option(cuisine_id : str) -> dict:
    return cuisine_id_dict[cuisine_id]

@tool(show_result=True)
def view_experience_option(experience_id : str) -> dict:
    return experience_id_dict[experience_id]

@tool(show_result=True)
def add_housing_option(housing_option: str):
    if housing_option in housing_id_dict:
        return "Housing option already exists"
    housing_agent.append(housing_option)
    return housing_agent

@tool(show_result=True)
def add_cuisine_option(cuisine_option: str):
    if cuisine_option in cuisine_id_dict:
        return "Cuisine option already exists"
    cuisine_agent.append(cuisine_option)
    return cuisine_agent

@tool(show_result=True)
def add_experience_option(experience_option: str):
    if experience_option in experience_id_dict:
        return "Experience option already exists"
    experience_agent.append(experience_option)
    return experience_agent

def build_context(user_preferences: Dict[str, Any], travel_info: Dict[str, Any]):
    housing_opts = filter_housing(user_preferences, travel_info)
    cuisine_opts = filter_cuisine(user_preferences, travel_info)
    experience_opts = filter_experiences(user_preferences, travel_info)
    print(f'housing_opts: {[x['id'] for x in housing_opts]}')
    print(f'cuisine_opts: {[x['id'] for x in cuisine_opts]}')
    print(f'experience_opts: {[x['id'] for x in experience_opts]}')

    # Keep context compact (IDs + a few fields). The model only needs IDs to choose.
    def slim(items, keep=("id", "name", "price", "tags")):
        return [{k: v for k, v in item.items() if k in keep} for item in items]

    ctx = {
        "UserPreferences": user_preferences,
        "TravelInfo": travel_info,
        "HousingOptions": slim(housing_opts),
        "CuisineOptions": slim(cuisine_opts),
        "ExperienceOptions": slim(experience_opts),
    }
    return ctx, housing_opts, cuisine_opts, experience_opts

def coerce_to_ListOut(text: str) -> ListOut:
    """
    Strictly parse JSON and validate with Pydantic. Raises on failure.
    """
    data = json.loads(text)
    return ListOut.model_validate(data)

def ai_travel_agent_agno(user_preferences: Dict[str, Any], travel_info: Dict[str, Any]) -> ListOut:
    context, housing_opts, cuisine_opts, experience_opts = build_context(user_preferences, travel_info)

    # Create the prompt. Put hard schema rules up front.
    SYSTEM_CONSTRAINTS = """
Here are the preferences of the user: {user_preferences}
Here are the travel information of the user: {travel_info}
Here are the housing options: {housing_opts}
Here are the cuisine options: {cuisine_opts}
Here are the experience options: {experience_opts}

You are an opportunities chooser model. You are not planning out the whole trip. Your job is to consider the possible housing, cuisine, and experience options avaialable, and if any of those look reasonably aligned with the user interests, track their ids.
Do the following
1. Look through the housing options and what they entail using the view_housing_option tool. If they seem to match the user's preferences, store them in housing_agent using the add_housing_option tool.
2. Look through the cuisine options and what they entail using the view_cuisine_option tool. If they seem to match the user's preferences, store them in cuisine_agent using the add_cuisine_option tool.
3. Look through the experience options and what they entail using the view_experience_option tool. If they seem to match the user's preferences, store them in experience_agent using the add_experience_option tool.

Note that the housing ids are of the form "H#". The cuisine ids are of the form "C#". The experience ids are of the form "E#".

YOU MUST return output as **JSON ONLY** conforming to this schema:
{
  "housing_ids": [],   // str IDs from Housing Options
  "cuisine_ids": [],   // str IDs from Cuisine Options
  "experience_ids": [] // str IDs from Experience Options
}

Rules:
- Use only IDs that appear in the provided options (do not invent IDs).
- Do not include any extra fields or text.
- Never return an empty list for any of the fields, except housing_ids.
- Do not add comments or prose; return a single JSON object only.
"""

    agent = Agent(model=Claude(id="claude-opus-4-1-20250805"))
    # If Agno supports schema binding directly, keep this:
    agent.output_schema = ListOut  # (Nice-to-have; we still validate below)
    agent.tools = [view_housing_option, view_cuisine_option, view_experience_option, add_housing_option, add_cuisine_option, add_experience_option]
    agent.print_response(SYSTEM_CONSTRAINTS)

    # --- Attempt 1
    # raw = agent.run(prompt).content if hasattr(agent.run(prompt), "content") else agent.run(prompt)
    # try:
    #     out = coerce_to_ListOut(raw)
    # except Exception as e:
    #     # --- Attempt 2: repair by telling model the exact error and to re-output clean JSON
    #     repair_prompt = f"""
    #     The model output the following error: {e}
    #     Please repair the output and return the correct JSON.
    #     """
    #     raw = agent.run(repair_prompt).content if hasattr(agent.run(repair_prompt), "content") else agent.run(repair_prompt)
    #     try:
    #         out = coerce_to_ListOut(raw)
    #     except Exception as e:
    #         raise ValueError(f"Failed to parse AI response: {e}")
    # return out

if __name__ == "__main__":
    from preferences import user_preferences
    from travel_info import travel_info
    ai_travel_agent_agno(user_preferences, travel_info)

# def update_user_profile(user_profile, house, liked):
#     if liked:
#         for amenity in house.amenities:
#             user_profile['amenities'][amenity] += 1
#     else:
#         for amenity in house.amenities:
#             user_profile['amenities'][amenity] -= 1
#     # Save user_profile to DB

