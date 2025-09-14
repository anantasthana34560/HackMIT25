import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_travel_info(paragraph):
    """
    Extracts user preferences and travel information from a paragraph of text.
    Returns a dictionary with fields:
        - location
        - dates
        - desired_amenities
        - total_budget
        - travelers
        - housing_type
        - preferred_amenities
        - safety_level
        - price_range
        - cuisine_types
        - experience_types
    """
    doc = nlp(paragraph)
    info = {
        "location": None,
        "dates": [],
        "desired_amenities": [],
        "total_budget": None,
        "travelers": None,
        "housing_type": [],
        "preferred_amenities": [],
        "safety_level": None,
        "price_range": [],
        "cuisine_types": [],
        "experience_types": []
    }

    # Extract location (GPE entities)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    if locations:
        info["location"] = locations[0]

    # Extract dates (DATE entities)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    info["dates"] = dates

    # Extract numbers for budget and travelers
    for ent in doc.ents:
        if ent.label_ == "MONEY":
            info["total_budget"] = ent.text
        if ent.label_ == "CARDINAL":
            # Heuristic: if "people" or "travelers" nearby, assign as travelers
            start = max(0, ent.start - 2)
            end = min(len(doc), ent.end + 2)
            window = doc[start:end].text.lower()
            if "people" in window or "traveler" in window or "person" in window:
                info["travelers"] = ent.text

    # Extract amenities, housing type, cuisine, experience, safety, price range
    amenities_keywords = ["wifi", "kitchen", "balcony", "pool", "air conditioning", "washing machine"]
    housing_keywords = ["house", "hotel", "apartment", "hostel"]
    cuisine_keywords = ["italian", "japanese", "chinese", "mexican", "indian", "french"]
    experience_keywords = ["adventure", "relaxation", "sightseeing", "culture", "nature"]
    safety_keywords = ["high", "medium", "low"]
    price_keywords = ["dollar", "usd", "$", "euro", "€"]

    tokens = [token.text.lower() for token in doc]

    # Amenities
    info["desired_amenities"] = [a for a in amenities_keywords if a in paragraph.lower()]
    info["preferred_amenities"] = info["desired_amenities"]

    # Housing type
    info["housing_type"] = [h.capitalize() for h in housing_keywords if h in paragraph.lower()]

    # Cuisine types
    info["cuisine_types"] = [c.capitalize() for c in cuisine_keywords if c in paragraph.lower()]

    # Experience types
    info["experience_types"] = [e.capitalize() for e in experience_keywords if e in paragraph.lower()]

    # Safety level
    for s in safety_keywords:
        if s in paragraph.lower() and "safety" in paragraph.lower():
            info["safety_level"] = s.capitalize()

    # Price range (look for patterns like "$50-$150" or "between 50 and 150 dollars")
    import re
    price_pattern = re.search(r"\$?(\d+)[\s\-toand]+(\d+)\s*(dollars|usd|\$)?", paragraph.lower())
    if price_pattern:
        info["price_range"] = [int(price_pattern.group(1)), int(price_pattern.group(2))]

    return info

# Example usage:
if __name__ == "__main__":
    paragraph = (
        "We are two travelers looking to visit Boston from February 10 to February 12. "
        "We'd like a hotel or house with WiFi and a kitchen, and our total budget is $500. "
        "We prefer Italian or Japanese food, want a high safety level, and are interested in adventure experiences. "
        "Our price range per night is between 50 and 150 dollars."
    )
    extracted = extract_travel_info(paragraph)
    print(extracted)