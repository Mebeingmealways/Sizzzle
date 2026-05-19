from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Booking, BookingDish, Dish, User, CookProfile, Review, db
from datetime import datetime, date, timedelta, timezone
import secrets
import string

bookings_bp = Blueprint('bookings', __name__)


def generate_booking_code():
    chars = string.ascii_uppercase + string.digits
    return 'BK-' + ''.join(secrets.choice(chars) for _ in range(6))


def generate_otp():
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def utc_now_naive():
    # Use timezone-aware current UTC time, then store as naive for existing schema compatibility.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _has_other_in_progress(cook_id, booking_id=None):
    query = Booking.query.filter_by(cook_id=cook_id, status='in_progress')
    if booking_id is not None:
        query = query.filter(Booking.id != booking_id)
    return db.session.query(query.exists()).scalar()


def _is_booking_cook_user(booking, user_id):
    cook_profile = CookProfile.query.filter_by(user_id=user_id).first()
    return bool(cook_profile and cook_profile.id == booking.cook_id)


@bookings_bp.route('', methods=['GET'])
@jwt_required()
def list_bookings():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    status = request.args.get('status')

    if user.role == 'customer':
        query = Booking.query.filter_by(customer_id=user_id)
    elif user.role == 'cook':
        cook_profile = CookProfile.query.filter_by(user_id=user_id).first()
        if not cook_profile:
            return jsonify({'error': 'Cook profile not found'}), 404
        query = Booking.query.filter_by(cook_id=cook_profile.id)
    else:
        query = Booking.query

    if status:
        query = query.filter_by(status=status)

    bookings = query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])


@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('cook_id') or not data.get('date'):
        return jsonify({'error': 'Cook and date required'}), 400

    try:
        booking_date = date.fromisoformat(data['date'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if booking_date <= date.today():
        return jsonify({'error': 'Booking must be at least 1 day in advance'}), 400

    cook = db.session.get(CookProfile, data['cook_id'])
    if not cook or cook.verification_status != 'approved':
        return jsonify({'error': 'Cook not available'}), 404

    booking = Booking(
        booking_code=generate_booking_code(),
        customer_id=user_id,
        cook_id=data['cook_id'],
        date=booking_date,
        time_slot=data.get('time_slot'),
        num_people=data.get('num_people', 1),
        tier=data.get('tier', 'standard'),
        total_amount=data.get('total_amount', 0),
        otp_code=generate_otp(),
        notes=data.get('notes'),
        address=data.get('address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )

    fee_rate = 0.12 if booking.tier == 'premium' else 0.15
    booking.platform_fee = round(booking.total_amount * fee_rate, 2)
    gst_rate = 0.05
    booking.cook_earnings = round(booking.total_amount - booking.platform_fee - (booking.total_amount * gst_rate), 2)

    db.session.add(booking)
    db.session.flush()

    for dish_id in data.get('dish_ids', []):
        if db.session.get(Dish, dish_id):
            db.session.add(BookingDish(booking_id=booking.id, dish_id=dish_id))

    db.session.commit()
    return jsonify(booking.to_dict()), 201


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    data = booking.to_dict()
    if booking.review:
        data['review'] = booking.review.to_dict()
    if booking.status in ('accepted', 'in_progress'):
        cook = db.session.get(CookProfile, booking.cook_id)
        if cook and cook.latitude is not None and cook.longitude is not None:
            data['cook_location'] = {
                'latitude': cook.latitude,
                'longitude': cook.longitude,
                'accuracy_m': cook.location_accuracy_m,
                'updated_at': cook.location_updated_at.isoformat() if cook.location_updated_at else None
            }
    return jsonify(data)


@bookings_bp.route('/<int:booking_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(booking_id):
    user_id = int(get_jwt_identity())
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    data = request.get_json()
    new_status = data.get('status')

    valid_transitions = {
        'pending': ['accepted', 'cancelled'],
        'accepted': ['in_progress', 'cancelled'],
        'in_progress': ['completed'],
    }

    allowed = valid_transitions.get(booking.status, [])
    if new_status not in allowed:
        return jsonify({'error': f'Cannot transition from {booking.status} to {new_status}'}), 400

    if new_status == 'in_progress':
        if not _is_booking_cook_user(booking, user_id):
            return jsonify({'error': 'Only assigned cook can start this service'}), 403
        if _has_other_in_progress(booking.cook_id, booking.id):
            return jsonify({'error': 'Complete current in-progress booking before starting another'}), 400

    booking.status = new_status
    if new_status == 'in_progress':
        booking.service_started_at = utc_now_naive()
    elif new_status == 'completed':
        booking.service_ended_at = utc_now_naive()
        cook = db.session.get(CookProfile, booking.cook_id)
        if cook:
            cook.total_jobs = (cook.total_jobs or 0) + 1
            cook.total_earnings = (cook.total_earnings or 0) + booking.cook_earnings

    db.session.commit()
    return jsonify(booking.to_dict())


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.customer_id != user_id:
        user = db.session.get(User, user_id)
        cook_profile = CookProfile.query.filter_by(user_id=user_id).first()
        if not cook_profile or cook_profile.id != booking.cook_id:
            return jsonify({'error': 'Unauthorized'}), 403

    if booking.status not in ('pending', 'accepted'):
        return jsonify({'error': 'Cannot cancel this booking'}), 400

    now = utc_now_naive()
    try:
        service_time = datetime.combine(booking.date, datetime.strptime(booking.time_slot or '12:00', '%H:%M').time())
    except (ValueError, TypeError):
        service_time = datetime.combine(booking.date, datetime.strptime('12:00', '%H:%M').time())
    hours_until = (service_time - now).total_seconds() / 3600

    if hours_until > 12:
        charge = 0
    elif hours_until > 6:
        charge = round(booking.total_amount * 0.50, 2)
    else:
        charge = round(booking.total_amount * 0.80, 2)

    booking.status = 'cancelled'
    booking.cancelled_at = now
    booking.cancellation_charge = charge
    db.session.commit()

    return jsonify({
        'booking': booking.to_dict(),
        'cancellation_charge': charge,
        'message': f'Booking cancelled. Charge: Rs {charge}'
    })


@bookings_bp.route('/<int:booking_id>/verify-otp', methods=['POST'])
@jwt_required()
def verify_otp(booking_id):
    user_id = int(get_jwt_identity())
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    if not _is_booking_cook_user(booking, user_id):
        return jsonify({'error': 'Only assigned cook can verify OTP'}), 403
    if booking.status != 'accepted':
        return jsonify({'error': 'Booking must be accepted before OTP verification'}), 400
    if _has_other_in_progress(booking.cook_id, booking.id):
        return jsonify({'error': 'Complete current in-progress booking before starting another'}), 400
    data = request.get_json()
    if data.get('otp') == booking.otp_code:
        booking.status = 'in_progress'
        booking.service_started_at = utc_now_naive()
        db.session.commit()
        return jsonify({'verified': True, 'booking': booking.to_dict()})
    return jsonify({'verified': False, 'error': 'Invalid OTP'}), 400


@bookings_bp.route('/<int:booking_id>/start', methods=['POST'])
@jwt_required()
def start_service(booking_id):
    user_id = int(get_jwt_identity())
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    if not _is_booking_cook_user(booking, user_id):
        return jsonify({'error': 'Only assigned cook can start this service'}), 403
    if booking.status != 'accepted':
        return jsonify({'error': 'Booking must be accepted first'}), 400
    if _has_other_in_progress(booking.cook_id, booking.id):
        return jsonify({'error': 'Complete current in-progress booking before starting another'}), 400
    booking.status = 'in_progress'
    booking.service_started_at = utc_now_naive()
    db.session.commit()
    return jsonify(booking.to_dict())


@bookings_bp.route('/<int:booking_id>/end', methods=['POST'])
@jwt_required()
def end_service(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    if booking.status != 'in_progress':
        return jsonify({'error': 'Service not in progress'}), 400
    booking.status = 'completed'
    booking.service_ended_at = utc_now_naive()
    cook = db.session.get(CookProfile, booking.cook_id)
    if cook:
        cook.total_jobs = (cook.total_jobs or 0) + 1
        cook.total_earnings = (cook.total_earnings or 0) + booking.cook_earnings
    db.session.commit()
    return jsonify(booking.to_dict())


@bookings_bp.route('/<int:booking_id>/rate', methods=['POST'])
@jwt_required()
def rate_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.customer_id != user_id:
        return jsonify({'error': 'Only the customer can rate'}), 403
    if booking.status != 'completed':
        return jsonify({'error': 'Can only rate completed bookings'}), 400
    if booking.review:
        return jsonify({'error': 'Already rated'}), 409

    data = request.get_json()
    rating = data.get('rating')
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be 1-5'}), 400

    review = Review(
        booking_id=booking.id,
        customer_id=user_id,
        cook_id=booking.cook_id,
        rating=rating,
        comment=data.get('comment', '')
    )
    db.session.add(review)

    cook = db.session.get(CookProfile, booking.cook_id)
    if cook:
        all_reviews = Review.query.filter_by(cook_id=cook.id).all()
        total = sum(r.rating for r in all_reviews) + rating
        count = len(all_reviews) + 1
        cook.rating = round(total / count, 1)

    db.session.commit()
    return jsonify(review.to_dict()), 201


@bookings_bp.route('/<int:booking_id>/cook-location', methods=['GET'])
@jwt_required()
def get_cook_location(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    if booking.status not in ('accepted', 'in_progress'):
        return jsonify({'error': 'Cook location only available for active bookings'}), 400
    cook = db.session.get(CookProfile, booking.cook_id)
    if not cook or cook.latitude is None or cook.longitude is None:
        return jsonify({'latitude': None, 'longitude': None, 'accuracy_m': None, 'updated_at': None})
    return jsonify({
        'latitude': cook.latitude,
        'longitude': cook.longitude,
        'accuracy_m': cook.location_accuracy_m,
        'updated_at': cook.location_updated_at.isoformat() if cook.location_updated_at else None
    })
