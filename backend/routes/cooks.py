from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import CookProfile, CookAvailability, User, Booking, Review, db
from datetime import datetime, timezone
from sqlalchemy import func

DAY_TO_INDEX = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

cooks_bp = Blueprint('cooks', __name__)


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@cooks_bp.route('', methods=['GET'])
def list_cooks():
    status = request.args.get('status', 'approved')
    specialization = request.args.get('specialization')

    query = CookProfile.query.filter_by(verification_status=status)
    if specialization:
        query = query.filter_by(specialization=specialization)

    cooks = query.all()
    return jsonify([c.to_dict() for c in cooks])


@cooks_bp.route('/<int:cook_id>', methods=['GET'])
def get_cook(cook_id):
    cook = CookProfile.query.get_or_404(cook_id)
    data = cook.to_dict()
    data['availability'] = [
        {'day': a.day_of_week, 'slot': a.slot, 'available': a.is_available}
        for a in cook.availability
    ]
    data['availability_schedule'] = cook.availability_schedule or []
    data['blocked_dates'] = cook.blocked_dates or []
    data['dishes'] = []
    for cd in cook.dishes:
        if cd.dish_id:
            from models import Dish
            dish = db.session.get(Dish, cd.dish_id)
            if dish:
                data['dishes'].append(dish.to_dict())
    return jsonify(data)


@cooks_bp.route('/<int:cook_id>/availability', methods=['PUT'])
@jwt_required()
def update_availability(cook_id):
    user_id = int(get_jwt_identity())
    cook = CookProfile.query.get_or_404(cook_id)
    if cook.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    CookAvailability.query.filter_by(cook_id=cook_id).delete()

    schedule = data.get('schedule') or []
    if not schedule and 'slots' in data:
        schedule = [
            {'day': entry.get('day'), 'active': True, 'slots': [entry.get('slot')]} 
            for entry in data.get('slots', []) if entry.get('day') and entry.get('slot')
        ]

    for entry in schedule:
        day_name = entry.get('day')
        day_index = DAY_TO_INDEX.get(day_name.title() if isinstance(day_name, str) else day_name)
        if day_index is None:
            continue
        if not entry.get('active', True):
            continue
        for slot in entry.get('slots', []):
            if slot:
                db.session.add(CookAvailability(
                    cook_id=cook_id,
                    day_of_week=day_index,
                    slot=slot,
                    is_available=True
                ))

    if 'travel_radius_km' in data:
        cook.travel_radius_km = data['travel_radius_km']
    elif 'travel_radius' in data:
        cook.travel_radius_km = data['travel_radius']

    if 'blocked_dates' in data:
        cook.blocked_dates = data['blocked_dates'] or []

    if 'schedule' in data or 'slots' in data:
        cook.availability_schedule = schedule

    db.session.commit()
    return jsonify({'message': 'Availability updated'})


@cooks_bp.route('/availability', methods=['PUT'])
@jwt_required()
def update_my_availability():
    user_id = int(get_jwt_identity())
    cook = CookProfile.query.filter_by(user_id=user_id).first()
    if not cook:
        return jsonify({'error': 'Cook profile not found'}), 404

    data = request.get_json() or {}
    CookAvailability.query.filter_by(cook_id=cook.id).delete()

    schedule = data.get('schedule') or []
    if not schedule and 'slots' in data:
        schedule = [
            {'day': entry.get('day'), 'active': True, 'slots': [entry.get('slot')]} 
            for entry in data.get('slots', []) if entry.get('day') and entry.get('slot')
        ]

    for entry in schedule:
        day_name = entry.get('day')
        day_index = DAY_TO_INDEX.get(day_name.title() if isinstance(day_name, str) else day_name)
        if day_index is None:
            continue
        if not entry.get('active', True):
            continue
        for slot in entry.get('slots', []):
            if slot:
                db.session.add(CookAvailability(
                    cook_id=cook.id,
                    day_of_week=day_index,
                    slot=slot,
                    is_available=True
                ))

    if 'travel_radius_km' in data:
        cook.travel_radius_km = data['travel_radius_km']
    elif 'travel_radius' in data:
        cook.travel_radius_km = data['travel_radius']

    if 'blocked_dates' in data:
        cook.blocked_dates = data['blocked_dates'] or []

    if 'schedule' in data or 'slots' in data:
        cook.availability_schedule = schedule

    db.session.commit()
    return jsonify({'message': 'Availability updated'})


@cooks_bp.route('/recommended', methods=['GET'])
@jwt_required()
def recommended_cooks():
    cooks = CookProfile.query.filter_by(verification_status='approved')\
        .order_by(CookProfile.rating.desc()).limit(6).all()
    return jsonify([c.to_dict() for c in cooks])


@cooks_bp.route('/recommend', methods=['POST'])
@jwt_required()
def smart_recommend():
    """Smart Cook Recommendation with Match Score (out of 100).
    Distance/Proximity: 30 pts, Quality: 30 pts, Verification: 20 pts, Personalization: 20 pts
    """
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())
    lat = data.get('latitude')
    lng = data.get('longitude')

    cooks = CookProfile.query.filter_by(verification_status='approved').all()
    results = []

    # Get user's taste profile for personalization
    from models import TasteProfile
    taste = TasteProfile.query.filter_by(user_id=user_id).first()

    for cook in cooks:
        # Skip cook if they have blocked the requested date
        if requested_date and cook.blocked_dates:
            try:
                import json
                blocked_dates = cook.blocked_dates if isinstance(cook.blocked_dates, list) else json.loads(cook.blocked_dates)
                if requested_date in blocked_dates:
                    continue  # Skip this cook
            except:
                pass  # If parsing fails, include the cook (fail-safe)

        score = 0
        distance_km = None

        # Distance score (30 pts) - closer is better
        if lat and lng and cook.latitude and cook.longitude:
            distance_km = CookProfile.haversine(lat, lng, cook.latitude, cook.longitude)
            if distance_km <= cook.travel_radius_km:
                score += max(0, 30 - (distance_km / cook.travel_radius_km) * 30)
        elif lat and lng:
            # Cook has no location, give partial score
            score += 10
        else:
            score += 15  # No location provided, neutral

        # Quality score (30 pts)
        if cook.rating:
            score += (cook.rating / 5.0) * 30

        # Verification score (20 pts)
        score += 20  # Already filtered to approved only

        # Personalization score (20 pts)
        if taste:
            # Check repeat bookings
            repeat = Booking.query.filter_by(
                customer_id=user_id, cook_id=cook.id
            ).filter(Booking.status == 'completed').count()
            score += min(10, repeat * 3)  # Up to 10 pts for repeats

            # Diet match - check if cook's specialization aligns
            score += 10  # Base personalization

        cook_data = cook.to_dict()
        cook_data['match_score'] = round(score, 1)
        cook_data['distance_km'] = round(distance_km, 1) if distance_km else None
        results.append(cook_data)

    results.sort(key=lambda x: x['match_score'], reverse=True)
    return jsonify(results[:10])


@cooks_bp.route('/location', methods=['POST'])
@jwt_required()
def update_location():
    """Update cook's real-time GPS location."""
    user_id = int(get_jwt_identity())
    cook = CookProfile.query.filter_by(user_id=user_id).first()
    if not cook:
        return jsonify({'error': 'Cook profile not found'}), 404

    data = request.get_json() or {}
    if data.get('latitude') is None or data.get('longitude') is None:
        return jsonify({'error': 'Latitude and longitude required'}), 400

    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (TypeError, ValueError):
        return jsonify({'error': 'Latitude and longitude must be numeric'}), 400

    if latitude < -90 or latitude > 90:
        return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
    if longitude < -180 or longitude > 180:
        return jsonify({'error': 'Longitude must be between -180 and 180'}), 400

    accuracy = data.get('accuracy_m')
    if accuracy is not None:
        try:
            accuracy = float(accuracy)
        except (TypeError, ValueError):
            return jsonify({'error': 'accuracy_m must be numeric'}), 400
        if accuracy < 0 or accuracy > 5000:
            return jsonify({'error': 'accuracy_m must be between 0 and 5000 meters'}), 400

    cook.latitude = latitude
    cook.longitude = longitude
    cook.location_accuracy_m = accuracy
    cook.location_updated_at = utc_now_naive()
    db.session.commit()

    return jsonify({
        'message': 'Location updated',
        'latitude': cook.latitude,
        'longitude': cook.longitude,
        'accuracy_m': cook.location_accuracy_m,
        'updated_at': cook.location_updated_at.isoformat()
    })


@cooks_bp.route('/earnings', methods=['GET'])
@jwt_required()
def cook_earnings():
    user_id = int(get_jwt_identity())
    cook = CookProfile.query.filter_by(user_id=user_id).first()
    if not cook:
        return jsonify({'error': 'Cook profile not found'}), 404

    completed = Booking.query.filter_by(cook_id=cook.id, status='completed').all()

    total_earned = sum(b.cook_earnings for b in completed)
    total_bookings = len(completed)

    # Calculate this week earnings
    from datetime import timedelta, date as date_type
    today = date_type.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    this_week_earnings = sum(
        b.cook_earnings for b in completed
        if week_start <= b.date <= week_end
    )
    
    # Weekly breakdown (last 7 days from week start)
    weekly_earnings = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_total = sum(
            b.cook_earnings for b in completed
            if b.date == day
        )
        weekly_earnings.append({
            'day': day.strftime('%a'),
            'week': day.strftime('%a'),
            'date': day.isoformat(),
            'amount': round(day_total, 2),
            'earned': round(day_total, 2)
        })

    pending_payout = this_week_earnings

    month_start = today.replace(day=1)
    this_month = sum(
        b.cook_earnings for b in completed
        if b.date and b.date >= month_start
    )
    # Recent payouts (simulated from completed bookings)
    payouts = []
    for b in completed[:5]:
        payouts.append({
            'id': b.id,
            'date': b.date.isoformat(),
            'amount': round(b.cook_earnings, 2),
            'booking_code': b.booking_code,
            'status': 'paid',
            'method': cook.payout_frequency or 'Weekly'
        })

    return jsonify({
        'total_earned': round(total_earned, 2),
        'this_week': round(this_week_earnings, 2),
        'pending_payout': round(pending_payout, 2),
        'total_bookings': total_bookings,
        'total_jobs': total_bookings,
        'average_per_job': round(total_earned / total_bookings, 2) if total_bookings else 0,
        'rating': cook.rating,
        'this_month': round(this_month, 2),
        'weekly_earnings': weekly_earnings,
        'weekly': weekly_earnings,
        'payouts': payouts,
        'payout_frequency': cook.payout_frequency
    })


@cooks_bp.route('/jobs', methods=['GET'])
@jwt_required()
def cook_jobs():
    user_id = int(get_jwt_identity())
    cook = CookProfile.query.filter_by(user_id=user_id).first()
    if not cook:
        return jsonify({'error': 'Cook profile not found'}), 404

    status = request.args.get('status')
    query = Booking.query.filter_by(cook_id=cook.id)
    if status:
        query = query.filter_by(status=status)

    jobs = query.order_by(Booking.date.desc()).all()
    result = []
    for b in jobs:
        customer = db.session.get(User, b.customer_id)
        job = b.to_dict()
        job['customer_name'] = customer.name if customer else None
        job['customer_phone'] = customer.phone if customer else None
        job['customer_address'] = customer.address if customer else None
        job['review'] = b.review.to_dict() if b.review else None
        result.append(job)

    return jsonify(result)
