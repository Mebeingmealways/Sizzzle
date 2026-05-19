from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, CookProfile, Complaint, Booking, Review, db
from sqlalchemy import func

manager_bp = Blueprint('manager', __name__)


def require_manager():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role not in ('manager', 'admin'):
        return None
    return user


def _mask_value(value, reveal=4):
    if not value:
        return None
    s = str(value).strip()
    if len(s) <= reveal:
        return '*' * len(s)
    return ('*' * (len(s) - reveal)) + s[-reveal:]


def _cook_verification_payload(cook):
    user = cook.user
    address = user.address if user else None
    city = None
    if address:
        parts = [p.strip() for p in address.split(',') if p.strip()]
        city = parts[-1] if parts else None

    docs = {
        'aadhar_number': {
            'label': 'Aadhaar Number',
            'value_masked': _mask_value(cook.aadhar_number),
            'provided': bool(cook.aadhar_number),
        },
        'pan_number': {
            'label': 'PAN Number',
            'value_masked': _mask_value(cook.pan_number),
            'provided': bool(cook.pan_number),
        },
        'fssai_license': {
            'label': 'FSSAI License',
            'value_masked': _mask_value(cook.fssai_license),
            'provided': bool(cook.fssai_license),
        },
        'bank_account': {
            'label': 'Bank Account',
            'value_masked': _mask_value(cook.bank_account),
            'provided': bool(cook.bank_account),
        },
        'ifsc_code': {
            'label': 'IFSC Code',
            'value_masked': cook.ifsc_code,
            'provided': bool(cook.ifsc_code),
        },
        'upi_id': {
            'label': 'UPI ID',
            'value_masked': cook.upi_id,
            'provided': bool(cook.upi_id),
        },
    }

    checklist = [
        {
            'key': 'identity',
            'title': 'Identity Verification',
            'items': [
                {'label': 'Aadhaar submitted', 'ok': bool(cook.aadhar_number)},
                {'label': 'PAN submitted', 'ok': bool(cook.pan_number)},
            ],
        },
        {
            'key': 'professional',
            'title': 'Professional Verification',
            'items': [
                {'label': 'Specialization provided', 'ok': bool(cook.specialization)},
                {'label': 'Experience details provided', 'ok': bool(cook.experience_type and cook.years_experience is not None)},
                {'label': 'FSSAI submitted', 'ok': bool(cook.fssai_license)},
            ],
        },
        {
            'key': 'payout',
            'title': 'Payout Verification',
            'items': [
                {'label': 'Bank account submitted', 'ok': bool(cook.bank_account)},
                {'label': 'IFSC submitted', 'ok': bool(cook.ifsc_code)},
                {'label': 'UPI submitted', 'ok': bool(cook.upi_id)},
            ],
        },
    ]

    completed_checks = sum(1 for section in checklist for item in section['items'] if item['ok'])
    total_checks = sum(len(section['items']) for section in checklist)

    return {
        **cook.to_dict(),
        'status_label': (cook.verification_status or 'pending').capitalize(),
        'city': city,
        'applied_at': user.created_at.isoformat() if user and user.created_at else None,
        'address': address,
        'documents': docs,
        'checklist': checklist,
        'checks_completed': completed_checks,
        'checks_total': total_checks,
    }


@manager_bp.route('/verification-queue', methods=['GET'])
@jwt_required()
def verification_queue():
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    status = request.args.get('status', 'pending')
    cooks = CookProfile.query.filter_by(verification_status=status).all()
    return jsonify([_cook_verification_payload(c) for c in cooks])


@manager_bp.route('/verifications/pending', methods=['GET'])
@jwt_required()
def verifications_pending():
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403
    cooks = CookProfile.query.filter_by(verification_status='pending').all()
    return jsonify([_cook_verification_payload(c) for c in cooks])


@manager_bp.route('/verifications/<int:cook_id>', methods=['GET'])
@jwt_required()
def verification_detail(cook_id):
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    cook = CookProfile.query.get_or_404(cook_id)
    return jsonify(_cook_verification_payload(cook))


@manager_bp.route('/verifications/<int:cook_id>', methods=['POST'])
@jwt_required()
def verify_action(cook_id):
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    cook = CookProfile.query.get_or_404(cook_id)
    data = request.get_json()
    action = data.get('action', data.get('status'))
    if action in ('approved', 'approve'):
        cook.verification_status = 'approved'
        message = 'Cook approved successfully'
    elif action in ('rejected', 'reject'):
        cook.verification_status = 'rejected'
        message = 'Cook rejected'
    elif action in ('pending', 'send_for_verification', 'under_review'):
        cook.verification_status = 'pending'
        message = 'Cook sent for registration verification'
    else:
        return jsonify({'error': 'Action must be approve/reject/send_for_verification'}), 400

    db.session.commit()
    return jsonify({
        'message': message,
        'reason': data.get('reason'),
        'cook': _cook_verification_payload(cook),
    })


@manager_bp.route('/verify/<int:cook_id>', methods=['PATCH'])
@jwt_required()
def verify_cook(cook_id):
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    cook = CookProfile.query.get_or_404(cook_id)
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ('approved', 'rejected'):
        return jsonify({'error': 'Status must be approved or rejected'}), 400

    cook.verification_status = new_status
    db.session.commit()
    return jsonify(_cook_verification_payload(cook))


@manager_bp.route('/complaints', methods=['GET'])
@jwt_required()
def list_complaints():
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    status = request.args.get('status')
    query = Complaint.query
    if status:
        query = query.filter_by(status=status)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    payload = []
    for c in complaints:
        row = c.to_dict()
        customer = db.session.get(User, c.customer_id)
        cook = db.session.get(CookProfile, c.cook_id)
        row['customer_name'] = customer.name if customer else None
        row['cook_name'] = cook.user.name if cook and cook.user else None
        payload.append(row)
    return jsonify(payload)


@manager_bp.route('/complaints', methods=['POST'])
@jwt_required()
def create_complaint():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('booking_id') or not data.get('subject'):
        return jsonify({'error': 'Booking ID and subject required'}), 400

    booking = db.session.get(Booking, data['booking_id'])
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Allow only booking participants or managers/admin to file complaint.
    actor = db.session.get(User, user_id)
    actor_cook = CookProfile.query.filter_by(user_id=user_id).first()
    is_participant = booking.customer_id == user_id or (actor_cook and actor_cook.id == booking.cook_id)
    if not is_participant and (not actor or actor.role not in ('manager', 'admin')):
        return jsonify({'error': 'Unauthorized to raise complaint for this booking'}), 403

    complaint = Complaint(
        booking_id=booking.id,
        customer_id=booking.customer_id,
        cook_id=booking.cook_id,
        subject=data['subject'],
        description=data.get('description', ''),
        priority=data.get('priority', 'Medium')
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify(complaint.to_dict()), 201


@manager_bp.route('/complaints/<int:complaint_id>', methods=['PATCH'])
@jwt_required()
def update_complaint(complaint_id):
    manager = require_manager()
    if not manager:
        return jsonify({'error': 'Manager access required'}), 403

    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()

    if 'status' in data:
        complaint.status = data['status']
    if 'resolution_notes' in data:
        complaint.resolution_notes = data['resolution_notes']
    complaint.manager_id = manager.id

    db.session.commit()
    return jsonify(complaint.to_dict())


@manager_bp.route('/complaints/<int:complaint_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_complaint(complaint_id):
    manager = require_manager()
    if not manager:
        return jsonify({'error': 'Manager access required'}), 403

    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()

    complaint.status = data.get('status', 'Resolved')
    complaint.resolution_notes = data.get('resolution_notes', '')
    complaint.manager_id = manager.id
    db.session.commit()
    return jsonify(complaint.to_dict())


@manager_bp.route('/cooks', methods=['GET'])
@jwt_required()
def managed_cooks():
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    cooks = CookProfile.query.all()
    return jsonify([c.to_dict() for c in cooks])


@manager_bp.route('/cook-metrics', methods=['GET'])
@jwt_required()
def cook_metrics():
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    cooks = CookProfile.query.all()
    metrics = []
    for cook in cooks:
        completed = Booking.query.filter_by(cook_id=cook.id, status='completed').count()
        cancelled = Booking.query.filter_by(cook_id=cook.id, status='cancelled').count()
        reviews = Review.query.filter_by(cook_id=cook.id).count()
        user = cook.user
        city = None
        if user and user.address:
            parts = [p.strip() for p in user.address.split(',') if p.strip()]
            city = parts[-1] if parts else None
        metrics.append({
            **cook.to_dict(),
            'completed_bookings': completed,
            'cancelled_bookings': cancelled,
            'review_count': reviews,
            'city': city
        })
    return jsonify(metrics)


@manager_bp.route('/cooks/<int:cook_id>/status', methods=['PATCH'])
@jwt_required()
def set_cook_status(cook_id):
    if not require_manager():
        return jsonify({'error': 'Manager access required'}), 403

    cook = CookProfile.query.get_or_404(cook_id)
    data = request.get_json() or {}

    enabled = data.get('enabled')
    status = data.get('status')

    if enabled is not None:
        cook.verification_status = 'approved' if bool(enabled) else 'rejected'
    elif status in ('approved', 'pending', 'rejected'):
        cook.verification_status = status
    else:
        return jsonify({'error': 'Provide enabled boolean or valid status'}), 400

    db.session.commit()
    return jsonify(cook.to_dict())
