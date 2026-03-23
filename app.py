from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
import json
import secrets
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Password from environment variable or default
OWNER_PASSWORD = os.environ.get('OWNER_PASSWORD')

# Data file path
DATA_FILE = 'data.json'

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                'projects': [],
                'skills': [],
                'stats': {
                    'project_count': '—',
                    'download_count': '—',
                    'user_count': '—',
                    'visitor_count': '1337'
                },
                'personal': {
                    'name': 'XOTIIC',
                    'bio': 'Full-stack developer specializing in modern websites and powerful Discord bots.',
                    'status': 'Building the future'
                },
                'contact': {
                    'email': 'xotiic@example.com',
                    'discord': 'xotiic',
                    'github': 'github.com/xotiic',
                    'twitter': '@xotiic'
                },
                'terminal': {
                    'skills': 'HTML/CSS • JavaScript • Python • Discord.js'
                }
            }
    return {
        'projects': [],
        'skills': [],
        'stats': {
            'project_count': '—',
            'download_count': '—',
            'user_count': '—',
            'visitor_count': '0'
        },
        'personal': {
            'name': 'XOTIIC',
            'bio': 'Full-stack developer specializing in modern websites and powerful Discord bots.',
            'status': 'Building the future'
        },
        'contact': {
            'email': 'xotiic@example.com',
            'discord': 'xotiic',
            'github': 'github.com/xotiic',
            'twitter': '@xotiic'
        },
        'terminal': {
            'skills': 'HTML/CSS • JavaScript • Python • Discord.js'
        }
    }

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Update visitor count on each visit
def increment_visitor():
    data = load_data()
    current = data['stats'].get('visitor_count', '0')
    if current != '—':
        try:
            num = int(str(current).replace(',', ''))
            data['stats']['visitor_count'] = str(num + 1)
        except:
            data['stats']['visitor_count'] = '1'
    save_data(data)
    return data['stats']['visitor_count']

@app.route('/')
def index():
    """Serve the main page"""
    increment_visitor()
    return send_from_directory('.', 'index.html')

@app.route('/owner')
def owner_route():
    """Owner login page - served by frontend, but backend handles API"""
    return send_from_directory('.', 'index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get all data"""
    data = load_data()
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def update_data():
    """Update data - requires authentication"""
    auth = request.headers.get('Authorization')
    if auth != OWNER_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if data:
        # Update stats
        if 'stats' in data:
            for key, value in data['stats'].items():
                if value:
                    data['stats'][key] = value
        
        # Update personal info
        if 'personal' in data:
            for key, value in data['personal'].items():
                if value:
                    data['personal'][key] = value
        
        # Update contact
        if 'contact' in data:
            for key, value in data['contact'].items():
                if value:
                    data['contact'][key] = value
        
        # Update terminal
        if 'terminal' in data:
            for key, value in data['terminal'].items():
                if value:
                    data['terminal'][key] = value
        
        # Update projects
        if 'projects' in data:
            data['projects'] = data['projects']
        
        # Update skills
        if 'skills' in data:
            data['skills'] = data['skills']
        
        save_data(data)
        return jsonify({'success': True, 'message': 'Data saved successfully'})
    
    return jsonify({'error': 'No data provided'}), 400

@app.route('/api/visitor', methods=['GET'])
def get_visitor():
    """Get visitor count"""
    data = load_data()
    return jsonify({'count': data['stats'].get('visitor_count', '0')})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check for Render"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
