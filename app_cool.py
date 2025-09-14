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
from typing import List, Dict, Any, Set
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
    return [e for e in experience_listings if e.get("location") == location and e.get("keyword") in user_preferences["experience_types"]]

def filter_housing(user_preferences: Dict[str, Any], travel_info: Dict[str, Any]):
    location = travel_info["location"]
    # dates = travel_info.get("dates", [])
    # require all requested dates to be in scheduled_dates
    out = []
    for h in housing_listings:
        if h.get("location") != location:
            continue
        # if dates and not all(d in h.get("scheduled_dates", []) for d in dates):
        #     continue
        if h.get("housing_type") not in user_preferences["housing_type"] or user_preferences["housing_type"] == []:
            continue
        # Match amenities from travel_info (desired_amenities)
        desired = set(travel_info.get("desired_amenities", []))
        if desired and not desired.intersection(set(h.get("amenities", []))):
            continue
        out.append(h)
    return out

# ===== Agno Agent (Claude) =====
from agno.agent import Agent
from agno.models.anthropic import Claude
from tools.web_tools import search_events, get_weather
from user_store import get_user, update_user
from agno.tools import tool

housing_agent = []
cuisine_agent = []
experience_agent = []

@tool(show_result=True)
def view_housing_option(housing_id : str) -> dict:
    return housing_id_dict.get(housing_id, "No housing exists with this ID")

@tool(show_result=True)
def view_cuisine_option(cuisine_id : str) -> dict:
    return cuisine_id_dict.get(cuisine_id, "No cuisine exists with this ID")

@tool(show_result=True)
def view_experience_option(experience_id : str) -> dict:
    return experience_id_dict.get(experience_id, "No experience exists with this ID")

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
    # Debug prints (IDs only)
    print("housing_opts:", [x["id"] for x in housing_opts])
    print("cuisine_opts:", [x["id"] for x in cuisine_opts])
    print("experience_opts:", [x["id"] for x in experience_opts])

    # Keep context compact (IDs + a few fields). The model only needs IDs to choose.
    def slim(items, keep=("id", "location", "housing_type", "cuisine_type", "experience", "amenities", "safety")):
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

    # Shortlist to reduce hallucination space (top-N by simple preference signals)
    def score_h(h):
        score = 0
        if user_preferences.get("safety_level") and h.get("safety") == user_preferences.get("safety_level"):
            score += 2
        desired = set(travel_info.get("desired_amenities", []))
        score += len(desired.intersection(set(h.get("amenities", []))))
        return score
    housing_opts = sorted(housing_opts, key=score_h, reverse=True)[:10]
    cuisine_opts = cuisine_opts[:10]
    experience_opts = experience_opts[:10]

    valid_h: Set[str] = {h["id"] for h in housing_opts}
    valid_c: Set[str] = {c["id"] for c in cuisine_opts}
    valid_e: Set[str] = {e["id"] for e in experience_opts}

    # Few-shot example
    example_user = {
        "preferences": {"safety_level": "High", "price_range": [50,150], "cuisine_types": ["Italian"], "experience_types": ["tour"]},
        "travel_info": {"location": "Boston, USA", "dates": ["2025-02-10"]}
    }
    example_options = {
        "housing": [{"id": "H1", "safety": "High", "amenities": ["WiFi"]}, {"id": "H2", "safety": "Low", "amenities": []}],
        "cuisine": [{"id": "C1", "cuisine_type": "Italian"}, {"id": "C2", "cuisine_type": "Chinese"}],
        "experience": [{"id": "E1", "experience": "Freedom Trail Tour"}, {"id": "E2", "experience": "Museum"}]
    }
    example_output = {"housing_ids": ["H1"], "cuisine_ids": ["C1"], "experience_ids": ["E1"]}

    SYSTEM = (
        "Use only the provided options and return only JSON with housing_ids, cuisine_ids, experience_ids. No prose. "
        "If none fit, return empty arrays. You MUST call the view_* tools to inspect items before selecting."
    )

    USER = {
        "preferences": user_preferences,
        "travel_info": travel_info,
        "housing_options": [{"id": h["id"], "safety": h.get("safety"), "amenities": h.get("amenities", [])} for h in housing_opts],
        "cuisine_options": [{"id": c["id"], "cuisine_type": c.get("cuisine_type")} for c in cuisine_opts],
        "experience_options": [{"id": e["id"], "experience": e.get("experience")} for e in experience_opts],
        "schema": {"housing_ids": [], "cuisine_ids": [], "experience_ids": []},
        "few_shot_example": {"input": {"user": example_user, "options": example_options}, "output": example_output},
        "tool_requirement": "Call view_housing_option, view_cuisine_option, and view_experience_option for at least 3 total items before answering.",
    }

    # Track tool calls
    global housing_agent, cuisine_agent, experience_agent
    housing_agent.clear(); cuisine_agent.clear(); experience_agent.clear()

    agent = Agent(model=Claude(id="claude-opus-4-1-20250805"))
    agent.output_schema = ListOut
    agent.tools = [view_housing_option, view_cuisine_option, view_experience_option, add_housing_option, add_cuisine_option, add_experience_option]

    try:
        raw = agent.run(json.dumps(USER), system=SYSTEM)
        text = raw.content if hasattr(raw, "content") else str(raw)
        # Enforce minimum tool usage
        total_tool_uses = len(housing_agent) + len(cuisine_agent) + len(experience_agent)
        if total_tool_uses < 3:
            raise RuntimeError("Insufficient tool usage before answering.")
        out = coerce_to_ListOut(text)
    except Exception:
        # Fallback: choose top-3 from whitelists
        return ListOut(
            housing_ids=list(valid_h)[:3],
            cuisine_ids=list(valid_c)[:3],
            experience_ids=list(valid_e)[:3],
        )

    # Guardrail: keep only IDs we offered
    out.housing_ids = [i for i in out.housing_ids if i in valid_h]
    out.cuisine_ids = [i for i in out.cuisine_ids if i in valid_c]
    out.experience_ids = [i for i in out.experience_ids if i in valid_e]
    return out


def second_stage_agent(username: str, likes: Dict[str, List[str]], travel_info: Dict[str, Any]) -> Dict[str, Any]:
    """After swipes: build itinerary scaffold, packing list, events using tools, and update per-user memory state."""
    user_record = get_user(username)
    # Minimal state increment
    history = user_record.get('history', [])
    history.append({'likes': likes, 'travel_info': travel_info})
    update_user(username, {'history': history})

    system = (
        "Create a concise day-by-day itinerary outline from liked items, then propose a packing list tailored to location and dates, "
        "and list 3-5 relevant events or festivals. Keep JSON only with keys: itinerary, packing_list, events."
    )
    user = {
        'likes': likes,
        'travel_info': travel_info,
        'instructions': 'Use the tools get_weather and search_events to ground recommendations.'
    }

    agent = Agent(model=Claude(id="claude-opus-4-1-20250805"), tools=[get_weather, search_events])
    raw = agent.run(json.dumps(user), system=system)
    text = raw.content if hasattr(raw, 'content') else str(raw)
    # Best effort JSON load
    try:
        return json.loads(text)
    except Exception:
        return {'itinerary': [], 'packing_list': [], 'events': []}

if __name__ == "__main__":
    from preferences import user_preferences
    from travel_info import travel_info
    print(ai_travel_agent_agno(user_preferences, travel_info))

# def update_user_profile(user_profile, house, liked):
#     if liked:
#         for amenity in house.amenities:
#             user_profile['amenities'][amenity] += 1
#     else:
#         for amenity in house.amenities:
#             user_profile['amenities'][amenity] -= 1
#     # Save user_profile to DB

