import pandas as pd
import random

# --- Configuration ---
NUM_ROWS = 200
BOSTON_NEIGHBORHOODS = [
    "Allston", "Back Bay", "Bay Village", "Beacon Hill", "Brighton",
    "Charlestown", "Chinatown", "Dorchester", "Downtown", "East Boston",
    "Fenway-Kenmore", "Hyde Park", "Jamaica Plain", "Mattapan",
    "Mission Hill", "North End", "Roslindale", "Roxbury", "South Boston",
    "South End", "West End", "West Roxbury"
]
HOUSING_TYPES = ["Apartment", "House", "Condo", "Townhouse", "Loft"]
RENTAL_TYPES = ["Entire place", "Private room", "Shared room"]
AMENITIES_LIST = [
    "Kitchen", "Washer", "Dryer", "WiFi", "TV", "Air conditioning",
    "Heating", "Dedicated workspace", "Free parking", "Patio", "Gym",
    "Pool", "Hot tub", "Self check-in", "Pets allowed"
]
REVIEW_SNIPPETS = [
    "Spacious and central", "Quiet street", "Comfortable beds",
    "Great host, very responsive", "Clean and tidy", "Amazing view",
    "Close to public transport", "Perfect for a weekend getaway",
    "Felt like a home away from home", "Would definitely stay again",
    "The place was sparkling clean.", "Host provided great local tips.",
    "Easy check-in process.", "Great value for the price.",
    "Stylish and modern apartment."
]

# --- Data Generation ---
data = []
for _ in range(NUM_ROWS):
    housing_type = random.choice(HOUSING_TYPES)
    bedrooms = random.randint(1, 5)
    bathrooms = random.randint(1, max(1, bedrooms - 1))
    beds = random.randint(bedrooms, bedrooms * 2)
    rental_type = random.choice(RENTAL_TYPES)

    # Determine cost based on features
    base_cost = 80
    cost = base_cost + (bedrooms * 50) + (bathrooms * 25)
    if rental_type == "Private room":
        cost *= 0.6
    elif rental_type == "Shared room":
        cost *= 0.4
    cost += random.randint(-20, 20) # Add some noise
    cost = int(round(cost / 5) * 5) # Round to nearest 5

    listing = {
        "safety_rating": round(random.uniform(3.5, 5.0), 2),
        "neighborhood": random.choice(BOSTON_NEIGHBORHOODS),
        "housing_type": housing_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "beds": beds,
        "rental_type": rental_type,
        "cost_per_night": cost,
        "amenities": random.sample(AMENITIES_LIST, k=random.randint(4, 10)),
        "reviews": random.sample(REVIEW_SNIPPETS, k=random.randint(2, 5))
    }
    data.append(listing)

# --- Create and Save DataFrame ---
df = pd.DataFrame(data)

# Convert lists to strings for CSV compatibility
df['amenities'] = df['amenities'].apply(lambda x: ', '.join(x))
df['reviews'] = df['reviews'].apply(lambda x: '; '.join(x))
df['id'] = f'H{df.index + 1}'


# Save to a file
df.to_csv("boston_airbnb_data.csv", index=False)

print("Successfully generated boston_airbnb_data.csv with 200 listings.")


housing_listings = df.to_dict(orient='records')

housing_id_dict = {a['id']: a for a in housing_listings}