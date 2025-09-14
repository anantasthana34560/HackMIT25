import sqlite3
import hashlib
import json
from datetime import datetime
import os

class TravelDatabase:
    def __init__(self, db_path="travel_platform.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                address TEXT,
                city TEXT,
                state_province TEXT,
                country TEXT,
                postal_code TEXT,
                emergency_contact TEXT,
                emergency_phone TEXT,
                account_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                preferences_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Travel plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS travel_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_name TEXT,
                destination TEXT,
                travel_dates TEXT,
                plan_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, user_data):
        """Create a new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(user_data['password'])
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, 
                                 date_of_birth, address, city, state_province, country, 
                                 postal_code, emergency_contact, emergency_phone, account_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['email'], password_hash, user_data['first_name'], 
                user_data['last_name'], user_data.get('phone', ''),
                user_data.get('date_of_birth', ''), user_data.get('address', ''),
                user_data.get('city', ''), user_data.get('state_province', ''),
                user_data.get('country', ''), user_data.get('postal_code', ''),
                user_data.get('emergency_contact', ''), user_data.get('emergency_phone', ''),
                user_data.get('account_type', 'Traveler')
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError:
            return None  # Email already exists
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, first_name, last_name, email, city, country, account_type
            FROM users WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'email': user[3],
                'city': user[4],
                'country': user[5],
                'account_type': user[6]
            }
        return None
    
    def save_user_preferences(self, user_id, preferences):
        """Save user travel preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        preferences_json = json.dumps(preferences)
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preferences_data)
            VALUES (?, ?)
        ''', (user_id, preferences_json))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id):
        """Get user travel preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT preferences_data FROM user_preferences WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return {}
    
    def save_travel_plan(self, user_id, plan_name, destination, travel_dates, plan_data):
        """Save a complete travel plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        plan_json = json.dumps(plan_data)
        dates_json = json.dumps(travel_dates, default=str)
        
        cursor.execute('''
            INSERT INTO travel_plans (user_id, plan_name, destination, travel_dates, plan_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, plan_name, destination, dates_json, plan_json))
        
        conn.commit()
        conn.close()
    
    def get_user_travel_plans(self, user_id):
        """Get all travel plans for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, plan_name, destination, travel_dates, created_at
            FROM travel_plans WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        plans = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': plan[0],
                'name': plan[1],
                'destination': plan[2],
                'dates': json.loads(plan[3]),
                'created_at': plan[4]
            }
            for plan in plans
        ]
