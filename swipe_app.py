from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from app_cool import filter_housing, filter_cuisine, filter_experiences, ai_travel_agent
from preferences import user_preferences
from travel_info import travel_info

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Store user swipe data in session (in production, use a database)
def init_session():
    if 'liked_items' not in session:
        session['liked_items'] = {'housing': [], 'cuisine': [], 'experiences': []}
    if 'disliked_items' not in session:
        session['disliked_items'] = {'housing': [], 'cuisine': [], 'experiences': []}
    if 'current_category' not in session:
        session['current_category'] = 'housing'
    if 'current_index' not in session:
        session['current_index'] = {'housing': 0, 'cuisine': 0, 'experiences': 0}

@app.route('/')
def index():
    init_session()
    return render_template('swipe_interface.html')

@app.route('/api/get_recommendations')
def get_recommendations():
    init_session()
    
    # Get filtered recommendations for each category
    housing_options = filter_housing(user_preferences, travel_info)
    cuisine_options = filter_cuisine(user_preferences, travel_info)
    experience_options = filter_experiences(user_preferences, travel_info)
    
    recommendations = {
        'housing': housing_options,
        'cuisine': cuisine_options,
        'experiences': experience_options
    }
    
    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'current_category': session['current_category'],
        'current_indices': session['current_index']
    })

@app.route('/api/get_current_card')
def get_current_card():
    init_session()
    
    category = session['current_category']
    index = session['current_index'][category]
    
    # Get recommendations for current category
    if category == 'housing':
        options = filter_housing(user_preferences, travel_info)
    elif category == 'cuisine':
        options = filter_cuisine(user_preferences, travel_info)
    else:  # experiences
        options = filter_experiences(user_preferences, travel_info)
    
    if index >= len(options):
        # Move to next category or finish
        next_category = get_next_category(category)
        if next_category:
            session['current_category'] = next_category
            session['current_index'][next_category] = 0
            return get_current_card()
        else:
            return jsonify({
                'success': True,
                'finished': True,
                'message': 'All recommendations completed!'
            })
    
    current_item = options[index]
    current_item['category'] = category
    
    return jsonify({
        'success': True,
        'card': current_item,
        'category': category,
        'progress': {
            'current': index + 1,
            'total': len(options),
            'category': category
        }
    })

@app.route('/api/swipe', methods=['POST'])
def handle_swipe():
    init_session()
    
    data = request.json
    direction = data.get('direction')  # 'left' or 'right'
    category = session['current_category']
    index = session['current_index'][category]
    
    # Get current item
    if category == 'housing':
        options = filter_housing(user_preferences, travel_info)
    elif category == 'cuisine':
        options = filter_cuisine(user_preferences, travel_info)
    else:  # experiences
        options = filter_experiences(user_preferences, travel_info)
    
    if index < len(options):
        current_item = options[index]
        
        if direction == 'right':  # Liked
            session['liked_items'][category].append(current_item)
        else:  # Disliked
            session['disliked_items'][category].append(current_item)
        
        # Move to next item
        session['current_index'][category] += 1
    
    return jsonify({
        'success': True,
        'liked_count': len(session['liked_items'][category]),
        'disliked_count': len(session['disliked_items'][category])
    })

@app.route('/api/get_final_recommendations')
def get_final_recommendations():
    init_session()
    
    # Use AI agent to generate final itinerary based on liked items
    liked_summary = {
        'housing': session['liked_items']['housing'],
        'cuisine': session['liked_items']['cuisine'],
        'experiences': session['liked_items']['experiences']
    }
    
    prompt = f"Based on the user's liked items, create a detailed travel itinerary: {liked_summary}"
    
    try:
        final_itinerary = ai_travel_agent(prompt, user_preferences, travel_info)
        
        return jsonify({
            'success': True,
            'liked_items': liked_summary,
            'final_itinerary': final_itinerary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'liked_items': liked_summary
        })

@app.route('/api/reset_session')
def reset_session():
    session.clear()
    return jsonify({'success': True, 'message': 'Session reset'})

def get_next_category(current_category):
    categories = ['housing', 'cuisine', 'experiences']
    try:
        current_index = categories.index(current_category)
        if current_index < len(categories) - 1:
            return categories[current_index + 1]
    except ValueError:
        pass
    return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
