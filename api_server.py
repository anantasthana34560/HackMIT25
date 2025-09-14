from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from extractor import extract_travel_info
from app_cool import ai_travel_agent_agno, second_stage_agent
from housing_listings import housing_id_dict
from cuisine_listings import cuisine_id_dict
from experience_listings import experience_id_dict


class PlanIn(BaseModel):
    freeform_text: Optional[str] = None
    dates: Optional[List[str]] = None
    travelers: Optional[int] = None
    user_preferences: Optional[Dict[str, Any]] = None
    travel_info: Optional[Dict[str, Any]] = None


class ItineraryIn(BaseModel):
    username: Optional[str] = "guest"
    likes: Dict[str, List[str]]
    travel_info: Dict[str, Any]


class DetailsIn(BaseModel):
    housing_ids: List[str] = []
    cuisine_ids: List[str] = []
    experience_ids: List[str] = []


app = FastAPI(title="TravelEase API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True}


@app.post("/api/ai-plan")
def api_ai_plan(body: PlanIn) -> Dict[str, Any]:
    """Create curated ID lists for housing/cuisine/experiences.
    Accepts either explicit user_preferences + travel_info or a freeform_text + dates/travelers.
    """
    user_prefs = body.user_preferences
    travel_info = body.travel_info

    if not (user_prefs and travel_info):
        extracted = extract_travel_info(body.freeform_text or "")
        if body.dates:
            extracted["dates"] = body.dates
        if body.travelers is not None:
            extracted["travelers"] = body.travelers

        user_prefs = {
            "housing_type": extracted.get("housing_type", []) or ["House", "Apartment", "Hotel"],
            "preferred_amenities": extracted.get("desired_amenities", []),
            "safety_level": extracted.get("safety_level") or "High",
            "price_range": extracted.get("price_range", [50, 150]),
            "cuisine_types": extracted.get("cuisine_preferences", []),
            "experience_types": extracted.get("experience_preferences", []),
        }
        travel_info = {
            "location": extracted.get("location") or "Boston, USA",
            "dates": extracted.get("dates", []),
            "desired_amenities": extracted.get("desired_amenities", []),
            "total_budget": extracted.get("total_budget", 0),
            "travelers": extracted.get("travelers", 1),
            "cuisine_preferences": extracted.get("cuisine_preferences", []),
            "experience_preferences": extracted.get("experience_preferences", []),
        }

    recs = ai_travel_agent_agno(user_prefs, travel_info)
    return {
        "success": True,
        "housing_ids": recs.housing_ids,
        "cuisine_ids": recs.cuisine_ids,
        "experience_ids": recs.experience_ids,
        "user_preferences": user_prefs,
        "travel_info": travel_info,
    }


@app.post("/api/itinerary")
def api_itinerary(body: ItineraryIn) -> Dict[str, Any]:
    data = second_stage_agent(body.username or "guest", body.likes, body.travel_info)
    return {"success": True, **data}


@app.post("/api/details")
def api_details(body: DetailsIn) -> Dict[str, Any]:
    def pick(obj: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        return {k: obj.get(k) for k in keys if k in obj}

    housing = []
    for _id in body.housing_ids:
        h = housing_id_dict.get(_id)
        if h:
            housing.append({
                "id": _id,
                **pick(h, [
                    "housing_type", "neighborhood", "location", "amenities", "safety", "safety_rating", "reviews"
                ])
            })

    cuisine = []
    for _id in body.cuisine_ids:
        c = cuisine_id_dict.get(_id)
        if c:
            cuisine.append({
                "id": _id,
                **pick(c, ["name", "cuisine_type", "location", "pricing"])
            })

    experience = []
    for _id in body.experience_ids:
        e = experience_id_dict.get(_id)
        if e:
            experience.append({
                "id": _id,
                **pick(e, ["experience", "location", "keyword"])
            })

    return {"success": True, "housing": housing, "cuisine": cuisine, "experience": experience}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)


