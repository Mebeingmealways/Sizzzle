from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, TasteProfile, CookProfile, db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = user.to_dict()

    if user.role == 'cook' and user.cook_profile:
        data['cook_profile'] = user.cook_profile.to_dict()

    if user.taste_profile:
        data['taste_profile'] = user.taste_profile.to_dict()

    return jsonify(data)


@profile_bp.route('', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']
    if 'latitude' in data:
        user.latitude = data['latitude']
    if 'longitude' in data:
        user.longitude = data['longitude']
    if 'notification_preferences' in data:
        prefs = data['notification_preferences'] or {}
        user.notification_preferences = {
            'booking_confirmations': bool(prefs.get('booking_confirmations', False)),
            'cook_arrival_alerts': bool(prefs.get('cook_arrival_alerts', False)),
            'promotional_offers': bool(prefs.get('promotional_offers', False))
        }

    # Handle cook profile fields
    if user.role == 'cook' and user.cook_profile:
        if 'specialization' in data:
            user.cook_profile.specialization = data['specialization']
        if 'experience_type' in data:
            user.cook_profile.experience_type = data['experience_type']
        if 'years_experience' in data:
            user.cook_profile.years_experience = data['years_experience']
        if 'bank_account' in data:
            user.cook_profile.bank_account = data['bank_account']
        if 'ifsc_code' in data:
            user.cook_profile.ifsc_code = data['ifsc_code']
        if 'upi_id' in data:
            user.cook_profile.upi_id = data['upi_id']
        if 'pan_number' in data:
            user.cook_profile.pan_number = data['pan_number']

    # Cook-specific profile fields can be updated from cook portal tabs.
    if user.role == 'cook':
        cook = CookProfile.query.filter_by(user_id=user_id).first()
        if cook:
            if 'specialization' in data:
                cook.specialization = data['specialization']
            if 'experience_type' in data:
                cook.experience_type = data['experience_type']
            if 'years_experience' in data:
                try:
                    cook.years_experience = int(data['years_experience'])
                except (TypeError, ValueError):
                    pass
            if 'bank_account' in data:
                cook.bank_account = data['bank_account']
            if 'ifsc_code' in data:
                cook.ifsc_code = data['ifsc_code']
            if 'pan_number' in data:
                cook.pan_number = data['pan_number']
            if 'upi_id' in data:
                cook.upi_id = data['upi_id']
            if 'payout_frequency' in data:
                cook.payout_frequency = data['payout_frequency']

    db.session.commit()
    
    # Return response with cook_profile included for cooks
    response_data = user.to_dict()
    if user.role == 'cook' and user.cook_profile:
        response_data['cook_profile'] = user.cook_profile.to_dict()
    return jsonify(response_data)


@profile_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()

    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400

    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401

    if len(data['new_password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'})


@profile_bp.route('/taste', methods=['GET'])
@jwt_required()
def get_taste():
    user_id = int(get_jwt_identity())
    taste = TasteProfile.query.filter_by(user_id=user_id).first()
    if not taste:
        return jsonify({'dietary_preferences': [], 'allergies': [], 'spice_level': 3, 'kitchen_equipment': []})
    return jsonify(taste.to_dict())


@profile_bp.route('/taste', methods=['PUT'])
@jwt_required()
def update_taste():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    taste = TasteProfile.query.filter_by(user_id=user_id).first()
    if not taste:
        taste = TasteProfile(user_id=user_id)
        db.session.add(taste)

    taste.dietary_preferences = data.get('dietary_preferences', [])
    taste.allergies = data.get('allergies', [])
    taste.spice_level = data.get('spice_level', 3)
    taste.kitchen_equipment = data.get('kitchen_equipment', [])

    db.session.commit()
    return jsonify(taste.to_dict())


@profile_bp.route('/kitchen-checklist', methods=['GET'])
@jwt_required()
def get_kitchen_checklist():
    user_id = int(get_jwt_identity())
    taste = TasteProfile.query.filter_by(user_id=user_id).first()
    if not taste:
        return jsonify({'kitchen_equipment': []})
    return jsonify({'kitchen_equipment': taste.kitchen_equipment or []})


@profile_bp.route('/kitchen-checklist', methods=['PUT'])
@jwt_required()
def update_kitchen_checklist():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    taste = TasteProfile.query.filter_by(user_id=user_id).first()
    if not taste:
        taste = TasteProfile(user_id=user_id)
        db.session.add(taste)

    taste.kitchen_equipment = data.get('kitchen_equipment', [])
    db.session.commit()
    return jsonify({'kitchen_equipment': taste.kitchen_equipment})
