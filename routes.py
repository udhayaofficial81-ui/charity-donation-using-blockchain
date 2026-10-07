from flask import Blueprint, request, jsonify, session
from blockchain import blockchain

api = Blueprint('api', __name__)

# ---- ADD DONATION ----
@api.route('/api/add_donation', methods=['POST'])
def add_donation():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    donor = data.get('donor')
    amount = data.get('amount')
    cause = data.get('cause')

    if not donor or not amount or not cause:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    blockchain.add_block({'donor': donor, 'amount': amount, 'cause': cause})
    return jsonify({'success': True, 'message': 'Donation added'})

# ---- VIEW CHAIN ----
@api.route('/api/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain)
