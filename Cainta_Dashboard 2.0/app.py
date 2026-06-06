from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cainta_secure_disaster_hub_key_2026'

# User Credential Registry Database Simulation
USERS_DB = {
    "admin": {"password": "1914", "role": "Admin", "name": "MDRRMO Chief"},
    "staff1": {"password": "staff", "role": "Staff", "name": "Felix Ave Operator"}
}

# Global Application Caches
system_settings = {
    "simulation_mode": True,
    "earthquake_vibration": 0.2,
    "fire_smoke_level": 180,
    "flood_water_level_cm": 15
}

announcements = [
    {"timestamp": "06:15 PM", "author": "MDRRMO Chief", "text": "Systems configured for active monsoon tracking near ICCT Cainta zone."}
]

chat_messages = [
    {"timestamp": "06:16 PM", "user": "System Bot", "text": "Secure operational communication log initialized."}
]

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# Protected Route: Accessible by authenticated Admin and Staff users
@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('landing_page', auth_failed='true'))
    return render_template('admin.html', user_role=session.get('role'), user_name=session.get('name'))

# API endpoint checking user security privileges on login
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if username in USERS_DB and USERS_DB[username]["password"] == password:
        session['logged_in'] = True
        session['username'] = username
        session['role'] = USERS_DB[username]["role"]
        session['name'] = USERS_DB[username]["name"]
        return jsonify({"status": "success", "role": session['role']})
    
    return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('landing_page'))

@app.route('/api/sensors')
def get_sensor_data():
    if system_settings["simulation_mode"]:
        system_settings["earthquake_vibration"] = round(random.uniform(0.1, 2.5), 2)
        system_settings["fire_smoke_level"] = random.randint(150, 320)
        system_settings["flood_water_level_cm"] = random.randint(0, 100)
    
    # Bundle live data feeds with announcements and chats for a unified update loop
    return jsonify({
        "telemetry": system_settings,
        "announcements": announcements,
        "chat": chat_messages
    })

@app.route('/api/admin/update', methods=['POST'])
def update_settings():
    if not session.get('logged_in') or session.get('role') != 'Admin':
        return jsonify({"status": "unauthorized"}), 403
        
    global system_settings
    data = request.json
    system_settings["simulation_mode"] = data.get("simulation_mode", True)
    system_settings["earthquake_vibration"] = float(data.get("earthquake_vibration", 0.2))
    system_settings["fire_smoke_level"] = int(data.get("fire_smoke_level", 180))
    system_settings["flood_water_level_cm"] = int(data.get("flood_water_level_cm", 15))
    return jsonify({"status": "success"})

@app.route('/api/admin/announce', methods=['POST'])
def post_announcement():
    if not session.get('logged_in') or session.get('role') != 'Admin':
        return jsonify({"status": "unauthorized"}), 403
    
    data = request.json
    text = data.get("text", "").strip()
    if text:
        announcements.insert(0, {
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "author": session.get('name'),
            "text": text
        })
    return jsonify({"status": "success"})

@app.route('/api/chat/send', methods=['POST'])
def send_chat():
    if not session.get('logged_in'):
        return jsonify({"status": "unauthorized"}), 403
        
    data = request.json
    text = data.get("text", "").strip()
    if text:
        chat_messages.append({
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "user": session.get('name'),
            "text": text
        })
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)