from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
import json
import os
import io
from fpdf import FPDF
import bcrypt
from extensions import socketio
from donation import donation_api
from blockchain import blockchain

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')  # Change this for production

CORS(app, resources={r"/*": {"origins": "*"}})
socketio.init_app(app, cors_allowed_origins='*')

app.register_blueprint(donation_api)

USERS_FILE = "users.json"

# ---------------------------
# User data helpers
# ---------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# ---------------------------
# Pages
# ---------------------------
@app.route('/')
def index():
    if 'email' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'email' not in session:
        return redirect('/')
    return render_template('home.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        users = load_users()
        if email in users:
            return jsonify({"success": False, "message": "Email already registered"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        users[email] = hashed_password
        save_users(users)

        return jsonify({"success": True, "message": "User registered successfully"}), 201

    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({"success": False, "message": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        users = load_users()
        if email not in users:
            return jsonify({"success": False, "message": "User not found"}), 401

        stored_hashed_password = users[email].encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            return jsonify({"success": False, "message": "Invalid password"}), 401

        session['email'] = email
        return jsonify({"success": True, "message": "Login successful", "redirect": "/home"}), 200

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"success": False, "message": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

# ---------------------------
# API Routes: Blockchain & Export
# ---------------------------
@app.route('/api/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain)

@app.route('/api/export_pdf', methods=['GET'])
def export_pdf():
    if 'email' not in session:
        return redirect('/')

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Charity Blockchain Ledger", ln=True, align='C')

    for block in blockchain.chain:
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt=(
            f"Block {block['index']}\n"
            f"Donor: {block['data'].get('donor', '')}\n"
            f"Amount: ₹{block['data'].get('amount', '')}\n"
            f"Cause: {block['data'].get('cause', '')}\n"
            f"Timestamp: {block['timestamp']}\n"
            f"Hash: {block['hash']}\n"
        ))

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', download_name='charity_blockchain.pdf', as_attachment=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
