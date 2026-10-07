from flask import Blueprint, render_template, request, redirect, session, send_file, jsonify
from blockchain import blockchain
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json
import os

donation_api = Blueprint('donation_api', __name__)
PROFILES_FILE = os.path.join(os.path.dirname(__file__), 'profiles.json')


def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE, 'r', encoding='utf-8') as profiles_file:
        return json.load(profiles_file)

# Dashboard UI
@donation_api.route('/dashboard', methods=['GET'])
def dashboard():
    if 'email' not in session:
        return redirect('/')
    return render_template('workspace.html')


@donation_api.route('/api/profile', methods=['GET', 'POST'])
def profile():
    email = session.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    profiles = load_profiles()
    if request.method == 'GET':
        details = profiles.get(email, {})
        return jsonify({
            'success': True,
            'profile': {
                'name': details.get('name', ''),
                'email': email,
                'phone': details.get('phone', ''),
                'organization': details.get('organization', ''),
                'address': details.get('address', '')
            }
        })

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'A valid profile is required'}), 400

    fields = ('name', 'phone', 'organization', 'address')
    details = {}
    for field in fields:
        value = data.get(field, '')
        if not isinstance(value, str) or len(value) > 200:
            return jsonify({'success': False, 'message': f'Invalid {field} value'}), 400
        details[field] = value.strip()

    profiles[email] = details
    with open(PROFILES_FILE, 'w', encoding='utf-8') as profiles_file:
        json.dump(profiles, profiles_file, indent=2)
    return jsonify({'success': True, 'message': 'Personal information saved'})

# JSON API - Get full blockchain
@donation_api.route('/api/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.get_chain())

# JSON API - Add new donation block
@donation_api.route('/api/add_donation', methods=['POST'])
def add_donation():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    donor = data.get('donor')
    amount = data.get('amount')
    cause = data.get('cause')

    if not donor or not amount or not cause:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    blockchain.add_block({'donor': donor, 'amount': amount, 'cause': cause})
    return jsonify({'success': True, 'message': 'Donation recorded'})

# PDF export
@donation_api.route('/export_pdf')
def export_pdf():
    os.makedirs("exports", exist_ok=True)
    filepath = "exports/donations.pdf"

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("Donation Records", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table headers
    data = [["Index", "Donor", "Amount", "Cause", "Timestamp", "Hash"]]

    for block in blockchain.get_chain()[1:]:
        bdata = block['data']
        data.append([
            str(block['index']),
            bdata.get('donor', ''),
            f"₹{bdata.get('amount', '')}",
            bdata.get('cause', ''),
            block['timestamp'],
            block['hash'][:10] + "..."
        ])

    # Define table and style
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4B8BBE')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)

    return send_file(filepath, as_attachment=True)
