import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import json
import os
from datetime import datetime
import openai
from geopy.geocoders import Nominatim
from googletrans import Translator
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
geolocator = Nominatim(user_agent="ai-travel-platform")
translator = Translator()
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class AITravelAgent:
    def __init__(self):
        self.activities_keywords = {
            'whales': ['whale watching', 'marine life', 'ocean tours', 'coastal'],
            'mountains': ['hiking', 'skiing', 'mountain views', 'alpine'],
            'beaches': ['beach', 'swimming', 'surfing', 'coastal'],
            'culture': ['museums', 'historic sites', 'art galleries', 'cultural'],
            'food': ['restaurants', 'local cuisine', 'food tours', 'culinary'],
            'adventure': ['extreme sports', 'adventure tours', 'outdoor activities'],
            'nightlife': ['bars', 'clubs', 'entertainment', 'nightlife'],
            'family': ['family-friendly', 'kids activities', 'theme parks']
        }

    def parse_travel_intent(self, query):
        """Parse natural language travel queries using AI"""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel intent parser. Extract location, activities, budget, dates, and group size from travel queries. Return JSON format."},
                    {"role": "user", "content": f"Parse this travel request: {query}"}
                ],
                max_tokens=200
            )
            return json.loads(response.choices[0].message.content)
        except:
            # Fallback parsing
            return self.fallback_parse(query)

    def fallback_parse(self, query):
        """Simple keyword-based parsing as fallback"""
        query_lower = query.lower()
        activities = []

        for activity, keywords in self.activities_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                activities.append(activity)

        return {
            'activities': activities,
            'location': None,
            'budget': None,
            'dates': None,
            'group_size': 1
        }

class AirbnbDataService:
    def __init__(self):
        self.base_url = "http://data.insideairbnb.com/united-states"
        self.sample_data = self.generate_sample_data()

    def generate_sample_data(self):
        """Generate sample Airbnb-like data for demonstration"""
        locations = [
            {'city': 'San Francisco', 'country': 'USA', 'lat': 37.7749, 'lng': -122.4194},
            {'city': 'New York', 'country': 'USA', 'lat': 40.7128, 'lng': -74.0060},
            {'city': 'Los Angeles', 'country': 'USA', 'lat': 34.0522, 'lng': -118.2437},
            {'city': 'Miami', 'country': 'USA', 'lat': 25.7617, 'lng': -80.1918},
            {'city': 'Seattle', 'country': 'USA', 'lat': 47.6062, 'lng': -122.3321},
        ]

        properties = []
        for i in range(50):
            location = random.choice(locations)
            properties.append({
                'id': f'prop_{i}',
                'name': f'Beautiful {random.choice(["Apartment", "House", "Condo", "Loft"])} in {location["city"]}',
                'city': location['city'],
                'country': location['country'],
                'latitude': location['lat'] + random.uniform(-0.1, 0.1),
                'longitude': location['lng'] + random.uniform(-0.1, 0.1),
                'price': random.randint(50, 500),
                'room_type': random.choice(['Entire home/apt', 'Private room', 'Shared room']),
                'accommodates': random.randint(1, 8),
                'bedrooms': random.randint(1, 4),
                'bathrooms': random.randint(1, 3),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'reviews': random.randint(0, 200),
                'host_id': f'host_{random.randint(1, 20)}',
                'safety_score': round(random.uniform(3.0, 5.0), 1),
                'amenities': random.sample(['WiFi', 'Kitchen', 'Parking', 'Pool', 'Gym', 'Pet-friendly', 'AC'], random.randint(2, 5)),
                'activities': random.sample(['whales', 'beaches', 'mountains', 'culture', 'food', 'nightlife'], random.randint(1, 3))
            })

        return properties

    def search_properties(self, filters):
        """Search properties based on filters"""
        results = self.sample_data.copy()

        if filters.get('city'):
            results = [p for p in results if filters['city'].lower() in p['city'].lower()]

        if filters.get('min_price'):
            results = [p for p in results if p['price'] >= filters['min_price']]

        if filters.get('max_price'):
            results = [p for p in results if p['price'] <= filters['max_price']]

        if filters.get('room_type'):
            results = [p for p in results if p['room_type'] == filters['room_type']]

        if filters.get('min_rating'):
            results = [p for p in results if p['rating'] >= filters['min_rating']]

        if filters.get('activities'):
            results = [p for p in results if any(activity in p['activities'] for activity in filters['activities'])]

        return results[:20]  # Limit results

class SafetyService:
    def get_safety_info(self, location):
        """Get safety information for a location"""
        # In a real implementation, this would integrate with travel advisory APIs
        safety_levels = ['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk']
        return {
            'overall_safety': random.choice(safety_levels),
            'crime_rate': round(random.uniform(1.0, 5.0), 1),
            'health_advisory': random.choice(['None', 'Vaccination recommended', 'Health precautions advised']),
            'current_events': [
                'Political stability maintained',
                'Tourist areas well-monitored',
                'Standard travel precautions recommended'
            ],
            'emergency_contacts': {
                'police': '911',
                'medical': '911',
                'tourist_helpline': '+1-800-TRAVEL'
            }
        }

# Initialize services
ai_agent = AITravelAgent()
airbnb_service = AirbnbDataService()
safety_service = SafetyService()

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Travel Platform API',
        'version': '1.0.0',
        'endpoints': [
            '/api/search',
            '/api/ai-agent',
            '/api/recommendations',
            '/api/safety',
            '/api/translate'
        ]
    })

@app.route('/api/search', methods=['POST'])
def search_properties():
    """Search for properties based on filters"""
    try:
        filters = request.json
        results = airbnb_service.search_properties(filters)

        return jsonify({
            'success': True,
            'count': len(results),
            'properties': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-agent', methods=['POST'])
def ai_travel_query():
    """Process natural language travel queries"""
    try:
        data = request.json
        query = data.get('query', '')
        preferences = data.get('preferences', {})
        
        # Check if this is a destination recommendation request
        if 'suggest' in query.lower() and 'destinations' in query.lower():
            # Use OpenAI to generate destination recommendations
            destination_input = preferences.get('destination_input', '')
            
            # Create a more specific prompt for destination recommendations
            prompt = f"""
            The user wants to travel to "{destination_input}". Please suggest 3 specific destinations that match this request.
            
            For each destination, provide:
            - name: The destination name and country
            - description: A compelling 1-2 sentence description
            - best_time: Best time to visit (e.g., "April-June, September-October")
            - avg_temp: Average temperature range (e.g., "15-25°C")
            
            Focus on destinations that are relevant to "{destination_input}". If they mentioned a country, suggest cities/regions within that country. If they mentioned a region, suggest specific places in that region.
            
            Return the response as a JSON array of objects with the above fields.
            """
            
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a travel expert providing destination recommendations. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                # Parse the AI response
                ai_content = response.choices[0].message.content.strip()
                
                # Try to extract JSON from the response
                import json
                try:
                    # Remove any markdown formatting
                    if '```json' in ai_content:
                        ai_content = ai_content.split('```json')[1].split('```')[0].strip()
                    elif '```' in ai_content:
                        ai_content = ai_content.split('```')[1].split('```')[0].strip()
                    
                    recommendations = json.loads(ai_content)
                    
                    return jsonify({
                        'success': True,
                        'query': query,
                        'recommendations': recommendations
                    })
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, return error
                    return jsonify({
                        'success': False,
                        'error': 'Failed to parse AI response',
                        'raw_response': ai_content
                    }), 500
                    
            except Exception as openai_error:
                return jsonify({
                    'success': False,
                    'error': f'OpenAI API error: {str(openai_error)}'
                }), 500
        
        else:
            # Original property search functionality
            intent = ai_agent.parse_travel_intent(query)
            
            search_filters = {}
            if intent.get('activities'):
                search_filters['activities'] = intent['activities']

            properties = airbnb_service.search_properties(search_filters)

            return jsonify({
                'success': True,
                'query': query,
                'intent': intent,
                'recommendations': properties[:10]
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get swipe-based trip recommendations"""
    try:
        data = request.json
        user_preferences = data.get('preferences', {})

        # Generate recommendations based on preferences
        all_properties = airbnb_service.sample_data

        # Simple recommendation algorithm
        recommendations = []
        for prop in all_properties:
            score = 0

            # Score based on activities
            if user_preferences.get('activities'):
                common_activities = set(prop['activities']) & set(user_preferences['activities'])
                score += len(common_activities) * 2

            # Score based on price preference
            if user_preferences.get('budget'):
                if prop['price'] <= user_preferences['budget']:
                    score += 1

            # Score based on rating
            score += prop['rating']

            prop['recommendation_score'] = score
            recommendations.append(prop)

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return jsonify({
            'success': True,
            'recommendations': recommendations[:10]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/safety', methods=['POST'])
def get_safety_info():
    """Get safety information for a location"""
    try:
        data = request.json
        location = data.get('location', '')

        safety_info = safety_service.get_safety_info(location)

        return jsonify({
            'success': True,
            'location': location,
            'safety_info': safety_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text to different languages"""
    try:
        data = request.json
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')

        translated = translator.translate(text, dest=target_language)

        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated.text,
            'source_language': translated.src,
            'target_language': target_language
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/social/connect', methods=['POST'])
def connect_travelers():
    """Connect solo travelers with similar interests"""
    try:
        data = request.json
        user_profile = data.get('profile', {})

        # Mock social matching
        potential_matches = [
            {
                'user_id': 'user_123',
                'name': 'Sarah M.',
                'age': 28,
                'interests': ['hiking', 'photography', 'local food'],
                'travel_style': 'adventure',
                'safety_verified': True,
                'mutual_connections': 2
            },
            {
                'user_id': 'user_456',
                'name': 'Mike T.',
                'age': 32,
                'interests': ['culture', 'museums', 'nightlife'],
                'travel_style': 'cultural',
                'safety_verified': True,
                'mutual_connections': 1
            }
        ]

        return jsonify({
            'success': True,
            'matches': potential_matches
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/booking', methods=['POST'])
def manage_booking():
    """Handle booking operations (create, cancel, modify)"""
    try:
        data = request.json
        action = data.get('action', '')
        booking_id = data.get('booking_id', '')

        if action == 'create':
            # Create new booking
            booking = {
                'booking_id': f'booking_{random.randint(1000, 9999)}',
                'property_id': data.get('property_id'),
                'check_in': data.get('check_in'),
                'check_out': data.get('check_out'),
                'guests': data.get('guests', 1),
                'total_price': data.get('total_price'),
                'status': 'confirmed',
                'created_at': datetime.now().isoformat()
            }

            return jsonify({
                'success': True,
                'booking': booking,
                'message': 'Booking created successfully'
            })

        elif action == 'cancel':
            return jsonify({
                'success': True,
                'booking_id': booking_id,
                'message': 'Booking cancelled successfully',
                'refund_amount': data.get('refund_amount', 0)
            })

        elif action == 'modify':
            return jsonify({
                'success': True,
                'booking_id': booking_id,
                'message': 'Booking modified successfully',
                'changes': data.get('changes', {})
            })

        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
