from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, CookProfile, Booking, Complaint, PlatformPolicy, BookingDish, Dish, db
from services.email_service import send_role_welcome_email
from services.notification_service import notify_user
from sqlalchemy import func
from datetime import date, timedelta

admin_bp = Blueprint('admin', __name__)


def require_admin():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'admin':
        return None
    return user


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def platform_stats():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    total_users = User.query.count()
    total_cooks = CookProfile.query.filter_by(verification_status='approved').count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(func.sum(Booking.platform_fee)).scalar() or 0
    open_disputes = Complaint.query.filter_by(status='Escalated').count()
    completed = Booking.query.filter_by(status='completed').count()
    cancelled = Booking.query.filter_by(status='cancelled').count()

    return jsonify({
        'total_users': total_users,
        'total_cooks': total_cooks,
        'total_bookings': total_bookings,
        'total_revenue': round(total_revenue, 2),
        'open_disputes': open_disputes,
        'completed_bookings': completed,
        'cancelled_bookings': cancelled
    })


@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
def analytics():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    period = request.args.get('period', '30d')
    try:
        days = int(period.replace('d', '')) if period.endswith('d') else 30
        days = max(1, min(days, 365))
    except (ValueError, TypeError):
        days = 30
    start_date = date.today() - timedelta(days=days)

    total_bookings = Booking.query.filter(Booking.date >= start_date).count()
    completed = Booking.query.filter(Booking.date >= start_date, Booking.status == 'completed').count()
    cancelled = Booking.query.filter(Booking.date >= start_date, Booking.status == 'cancelled').count()
    revenue = db.session.query(func.sum(Booking.platform_fee)).filter(
        Booking.date >= start_date, Booking.status == 'completed'
    ).scalar() or 0

    total_users = User.query.filter_by(role='customer').count()
    total_cooks = CookProfile.query.filter_by(verification_status='approved').count()
    pending_cooks = CookProfile.query.filter_by(verification_status='pending').count()
    open_complaints = Complaint.query.filter(Complaint.status.in_(['Open', 'Investigating'])).count()

    # City breakdown from booking addresses (last token after comma)
    def city_from_address(address):
        if not address:
            return 'Unknown'
        parts = [p.strip() for p in address.split(',') if p.strip()]
        return parts[-1] if parts else 'Unknown'

    bookings_in_period = Booking.query.filter(Booking.date >= start_date).all()
    city_counts = {}
    for b in bookings_in_period:
        city = city_from_address(b.address)
        city_counts[city] = city_counts.get(city, 0) + 1

    max_city = max(city_counts.values()) if city_counts else 1
    city_breakdown = [
        {
            'name': city,
            'bookings': count,
            'pct': round((count / max_city) * 100, 1) if max_city else 0
        }
        for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    ]

    # Top cuisines by ordered dishes in period
    cuisine_rows = db.session.query(
        Dish.cuisine,
        func.count(BookingDish.id)
    ).join(
        BookingDish, Dish.id == BookingDish.dish_id
    ).join(
        Booking, Booking.id == BookingDish.booking_id
    ).filter(
        Booking.date >= start_date
    ).group_by(
        Dish.cuisine
    ).order_by(
        func.count(BookingDish.id).desc()
    ).limit(6).all()

    cuisine_breakdown = [
        {'name': cuisine or 'Other', 'orders': int(count)}
        for cuisine, count in cuisine_rows
    ]

    # Revenue trend: completed booking platform fee over last 6 months
    this_month_start = date.today().replace(day=1)
    revenue_trend = []
    for offset in range(5, -1, -1):
        year = this_month_start.year
        month = this_month_start.month - offset
        while month <= 0:
            month += 12
            year -= 1

        month_start = date(year, month, 1)
        if month == 12:
            next_month_start = date(year + 1, 1, 1)
        else:
            next_month_start = date(year, month + 1, 1)

        month_revenue = db.session.query(func.sum(Booking.platform_fee)).filter(
            Booking.date >= month_start,
            Booking.date < next_month_start,
            Booking.status == 'completed'
        ).scalar() or 0

        revenue_trend.append({
            'month': month_start.strftime('%b'),
            'revenue': round(month_revenue, 2)
        })

    # Growth snapshot versus previous equal-duration window
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date

    def growth_percent(current, previous):
        if previous <= 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    current_new_customers = User.query.filter(
        User.role == 'customer',
        User.created_at >= start_date
    ).count()
    prev_new_customers = User.query.filter(
        User.role == 'customer',
        User.created_at >= prev_start,
        User.created_at < prev_end
    ).count()

    current_new_cooks = User.query.filter(
        User.role == 'cook',
        User.created_at >= start_date
    ).count()
    prev_new_cooks = User.query.filter(
        User.role == 'cook',
        User.created_at >= prev_start,
        User.created_at < prev_end
    ).count()

    current_new_managers = User.query.filter(
        User.role == 'manager',
        User.created_at >= start_date
    ).count()
    prev_new_managers = User.query.filter(
        User.role == 'manager',
        User.created_at >= prev_start,
        User.created_at < prev_end
    ).count()

    retention_current = round(completed / total_bookings * 100, 1) if total_bookings else 0.0
    prev_total = Booking.query.filter(
        Booking.date >= prev_start,
        Booking.date < prev_end
    ).count()
    prev_completed = Booking.query.filter(
        Booking.date >= prev_start,
        Booking.date < prev_end,
        Booking.status == 'completed'
    ).count()
    retention_previous = round(prev_completed / prev_total * 100, 1) if prev_total else 0.0

    growth = {
        'customers': {
            'value': total_users,
            'delta_pct': growth_percent(current_new_customers, prev_new_customers)
        },
        'cooks': {
            'value': total_cooks,
            'delta_pct': growth_percent(current_new_cooks, prev_new_cooks)
        },
        'managers': {
            'value': User.query.filter_by(role='manager').count(),
            'delta_pct': growth_percent(current_new_managers, prev_new_managers)
        },
        'retention_rate': {
            'value': retention_current,
            'delta_pct': round(retention_current - retention_previous, 1)
        }
    }

    # Daily breakdown
    daily = []
    for i in range(min(days, 14)):
        d = date.today() - timedelta(days=i)
        day_bookings = Booking.query.filter_by(date=d).count()
        day_revenue = db.session.query(func.sum(Booking.platform_fee)).filter(
            Booking.date == d, Booking.status == 'completed'
        ).scalar() or 0
        daily.append({
            'date': d.isoformat(),
            'bookings': day_bookings,
            'revenue': round(day_revenue, 2)
        })

    return jsonify({
        'total_bookings': total_bookings,
        'completed_bookings': completed,
        'cancelled_bookings': cancelled,
        'total_revenue': round(revenue, 2),
        'total_customers': total_users,
        'total_cooks': total_cooks,
        'pending_verifications': pending_cooks,
        'open_complaints': open_complaints,
        'daily': list(reversed(daily)),
        'city_breakdown': city_breakdown,
        'cuisine_breakdown': cuisine_breakdown,
        'revenue_trend': revenue_trend,
        'growth': growth,
        'completion_rate': round(completed / total_bookings * 100, 1) if total_bookings else 0,
        'cancellation_rate': round(cancelled / total_bookings * 100, 1) if total_bookings else 0
    })


@admin_bp.route('/managers', methods=['GET'])
@jwt_required()
def list_managers():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    managers = User.query.filter_by(role='manager').all()
    return jsonify([m.to_dict() for m in managers])


@admin_bp.route('/managers', methods=['POST'])
@jwt_required()
def create_manager():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        name=data.get('name', ''),
        email=data['email'],
        phone=data.get('phone'),
        role='manager',
        address=data.get('region')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    notify_user(
        user.id,
        title='Manager Access Granted',
        message='Your manager account has been created. You can now access the manager dashboard.',
        kind='account',
        entity_type='user',
        entity_id=user.id,
    )

    try:
        send_role_welcome_email(user)
    except Exception:
        pass
    return jsonify(user.to_dict()), 201


@admin_bp.route('/managers/<int:manager_id>/region', methods=['POST'])
@jwt_required()
def assign_region(manager_id):
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    manager = User.query.get_or_404(manager_id)
    if manager.role != 'manager':
        return jsonify({'error': 'Not a manager'}), 400

    data = request.get_json()
    manager.address = data.get('region', manager.address)
    db.session.commit()

    notify_user(
        manager.id,
        title='Region Assignment Updated',
        message=f'Your assigned region is now: {manager.address or "not specified"}.',
        kind='account',
        entity_type='user',
        entity_id=manager.id,
    )

    return jsonify(manager.to_dict())


@admin_bp.route('/policies', methods=['GET'])
@jwt_required()
def list_policies():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    policies = PlatformPolicy.query.all()
    return jsonify([{'id': p.id, 'key': p.key, 'value': p.value, 'description': p.description} for p in policies])


@admin_bp.route('/policies', methods=['PUT'])
@jwt_required()
def update_policies():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    for item in data.get('policies', []):
        policy = PlatformPolicy.query.filter_by(key=item['key']).first()
        if policy:
            policy.value = str(item['value'])
        else:
            db.session.add(PlatformPolicy(key=item['key'], value=str(item['value']), description=item.get('description', '')))
    db.session.commit()
    return jsonify({'message': 'Policies updated'})


@admin_bp.route('/policies/<int:policy_id>', methods=['PUT'])
@jwt_required()
def update_single_policy(policy_id):
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    policy = PlatformPolicy.query.get_or_404(policy_id)
    data = request.get_json()
    if 'value' in data:
        policy.value = str(data['value'])
    if 'description' in data:
        policy.description = data['description']
    db.session.commit()
    return jsonify({'id': policy.id, 'key': policy.key, 'value': policy.value, 'description': policy.description})


@admin_bp.route('/disputes', methods=['GET'])
@jwt_required()
def list_disputes():
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    disputes = Complaint.query.filter(
        Complaint.status.in_(['Escalated', 'Open', 'Investigating'])
    ).order_by(Complaint.created_at.desc()).all()
    return jsonify([c.to_dict() for c in disputes])


@admin_bp.route('/disputes/<int:dispute_id>', methods=['PATCH'])
@jwt_required()
def resolve_dispute(dispute_id):
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    complaint = Complaint.query.get_or_404(dispute_id)
    data = request.get_json()
    if 'status' in data:
        complaint.status = data['status']
    if 'resolution_notes' in data:
        complaint.resolution_notes = data['resolution_notes']
    db.session.commit()

    booking = complaint.booking
    booking_code = booking.booking_code if booking else f'#{complaint.booking_id}'
    notify_user(
        complaint.customer_id,
        title='Dispute Updated',
        message=f'Dispute #{complaint.id} for booking {booking_code} is now {complaint.status}.',
        kind='dispute',
        entity_type='complaint',
        entity_id=complaint.id,
    )
    cook_profile = db.session.get(CookProfile, complaint.cook_id)
    if cook_profile and cook_profile.user_id:
        notify_user(
            cook_profile.user_id,
            title='Dispute Updated',
            message=f'Dispute #{complaint.id} for booking {booking_code} is now {complaint.status}.',
            kind='dispute',
            entity_type='complaint',
            entity_id=complaint.id,
        )

    return jsonify(complaint.to_dict())


@admin_bp.route('/disputes/<int:dispute_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_dispute_post(dispute_id):
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403

    complaint = Complaint.query.get_or_404(dispute_id)
    data = request.get_json()
    complaint.status = data.get('status', 'Resolved')
    complaint.resolution_notes = data.get('resolution_notes', '')
    db.session.commit()

    booking = complaint.booking
    booking_code = booking.booking_code if booking else f'#{complaint.booking_id}'
    notify_user(
        complaint.customer_id,
        title='Dispute Resolved',
        message=f'Dispute #{complaint.id} for booking {booking_code} is now {complaint.status}.',
        kind='dispute',
        entity_type='complaint',
        entity_id=complaint.id,
    )
    cook_profile = db.session.get(CookProfile, complaint.cook_id)
    if cook_profile and cook_profile.user_id:
        notify_user(
            cook_profile.user_id,
            title='Dispute Resolved',
            message=f'Dispute #{complaint.id} for booking {booking_code} is now {complaint.status}.',
            kind='dispute',
            entity_type='complaint',
            entity_id=complaint.id,
        )

    return jsonify(complaint.to_dict())
