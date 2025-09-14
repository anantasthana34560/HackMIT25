import csv
import os


def _find_restaurants_csv(base_dir):
    for name in os.listdir(base_dir):
        lower = name.lower()
        if lower.endswith('.csv') and 'restaurant' in lower:
            return os.path.join(base_dir, name)
    return ""


def _normalize_location(default_city="Boston", default_country="USA"):
    return f"{default_city}, {default_country}"


def _price_bucket(min_price, max_price):
    try:
        lo = float(min_price) if min_price not in (None, "") else None
        hi = float(max_price) if max_price not in (None, "") else None
        avg = None
        if lo is not None and hi is not None:
            avg = (lo + hi) / 2.0
        elif lo is not None:
            avg = lo
        elif hi is not None:
            avg = hi
        else:
            return 'medium'
    except Exception:
        return 'medium'

    if avg <= 20:
        return 'low'
    if avg <= 50:
        return 'medium'
    if avg <= 90:
        return 'high'
    return 'ultra high'


def _load_cuisines_from_csv():
    base_dir = os.path.dirname(__file__)
    csv_path = _find_restaurants_csv(base_dir)
    results = []
    if not csv_path:
        return results

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        idx = 1
        for row in reader:
            # Restaurant name: first column is unnamed in provided CSV
            name = (row.get('') or row.get('Name') or row.get('Restaurant') or '').strip()
            cuisine_type = row.get('Cuisine Type', '').strip() or 'Unknown'
            min_price = row.get('Min Price ($)', '')
            max_price = row.get('Max Price ($)', '')
            pricing = _price_bucket(min_price, max_price)
            results.append({
                'id': f"C{idx}",
                'location': _normalize_location(),
                'name': name or cuisine_type,
                'cuisine_type': cuisine_type,
                'pricing': pricing,
            })
            idx += 1
    return results


cuisine_listings = _load_cuisines_from_csv()

if not cuisine_listings:
    cuisine_listings = [
        {"id": "C1", "location": "Boston, USA", "cuisine_type": "American", "pricing": "medium"},
        {"id": "C2", "location": "Boston, USA", "cuisine_type": "Italian", "pricing": "medium"},
        {"id": "C3", "location": "Boston, USA", "cuisine_type": "Chinese", "pricing": "low"},
    ]


cuisine_id_dict = {a['id']: a for a in cuisine_listings}