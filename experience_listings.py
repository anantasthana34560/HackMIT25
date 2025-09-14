import csv
import os


def _find_experiences_csv(base_dir):
    for name in os.listdir(base_dir):
        lower = name.lower()
        if lower.endswith('.csv') and 'experience' in lower:
            return os.path.join(base_dir, name)
    return ""


def _normalize_location(city_location, country):
    city = city_location.split(',')[0].strip() if city_location else ""
    country_norm = country.strip() if country else ""
    if country_norm.lower() in {"united states", "usa", "u.s.a.", "us", "u.s."}:
        country_norm = "USA"
    return f"{city}, {country_norm}" if city and country_norm else city or country_norm


def _price_bucket(cost_value):
    try:
        if isinstance(cost_value, (int, float)):
            cost = float(cost_value)
        else:
            txt = str(cost_value).strip()
            if txt.lower() == 'free':
                return 'low'
            cost = float(txt)
    except Exception:
        return 'medium'

    if cost <= 30:
        return 'low'
    if cost <= 80:
        return 'medium'
    if cost <= 150:
        return 'high'
    return 'ultra high'


def _categorize_keyword(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["comedy", "improv", "stand-up", "stand up", "laugh"]):
        return "Comedy"
    if any(k in t for k in ["class", "workshop", "lesson", "course", "lecture", "science", "robotics", "stem"]):
        return "Education"
    if any(k in t for k in ["museum", "exhibit", "gallery", "observatory", "planetarium"]):
        return "Museum"
    if any(k in t for k in ["kayak", "kayaking", "bike", "biking", "hike", "hiking", "adventure", "canoe", "zipline"]):
        return "Adventure"
    if any(k in t for k in ["historic", "history", "historical", "freedom trail", "old state", "colonial", "presidential", "tour of"]):
        return "Historic"
    if any(k in t for k in ["picnic", "tea", "relax", "quiet", "garden", "courtyard"]):
        return "Relaxing"
    if any(k in t for k in ["tour", "cruise", "view", "sightseeing", "panoramic", "observatory", "walk", "trail", "boat"]):
        return "Sightseeing"
    return "Sightseeing"


def _load_experiences_from_csv():
    base_dir = os.path.dirname(__file__)
    csv_path = _find_experiences_csv(base_dir)
    results = []
    if not csv_path:
        return results

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        idx = 1
        for row in reader:
            location = _normalize_location(row.get('City Location', ''), row.get('Country', ''))
            title = row.get('Experience Description') or row.get('Company Name') or 'Experience'
            pricing = _price_bucket(row.get('Cost ($)', ''))
            keyword = (row.get('Keyword') or '').strip()
            if not keyword:
                # Compute keyword if CSV lacks it
                keyword = _categorize_keyword(title or row.get('Company Name', ''))
            results.append({
                'id': f"E{idx}",
                'location': location,
                'experience': title,
                'pricing': pricing,
                'keyword': keyword,
            })
            idx += 1
    return results


experience_listings = _load_experiences_from_csv()

if not experience_listings:
    experience_listings = [
        {"id": "E1", "location": "Paris, France", "experience": "Eiffel Tower Tour", "pricing": "high", "keyword": "Sightseeing"},
        {"id": "E2", "location": "Paris, France", "experience": "Wine Tasting", "pricing": "medium", "keyword": "Relaxing"},
        {"id": "E3", "location": "Paris, France", "experience": "Seine River Cruise", "pricing": "medium", "keyword": "Sightseeing"},
        {"id": "E4", "location": "New York, USA", "experience": "Broadway Show", "pricing": "ultra high", "keyword": "Education"},
        {"id": "E5", "location": "New York, USA", "experience": "Central Park Picnic", "pricing": "low", "keyword": "Relaxing"},
        {"id": "E6", "location": "Tokyo, Japan", "experience": "Sushi Making Class", "pricing": "high", "keyword": "Education"},
        {"id": "E7", "location": "Tokyo, Japan", "experience": "Cherry Blossom Viewing", "pricing": "medium", "keyword": "Sightseeing"},
    ]


experience_id_dict = {a['id']: a for a in experience_listings}