from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from datetime import timedelta, timezone, datetime
import secrets
import string
from sqlalchemy.exc import SQLAlchemyError

from models import User, CookProfile, db
from services.email_service import send_verification_otp, send_role_welcome_email, send_password_reset_otp
from services.redis_store import set_otp, get_otp, delete_otp, redis_is_configured
from services.notification_service import notify_user

auth_bp = Blueprint('auth', __name__)


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_email_otp():
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def set_email_verification(user):
    user.email_verification_code = generate_email_otp()
    user.email_verification_sent_at = utc_now_naive()
    ttl = int(current_app.config.get('EMAIL_OTP_TTL_MINUTES', 10))
    user.email_verification_expires_at = user.email_verification_sent_at + timedelta(minutes=ttl)

    if redis_is_configured():
        set_otp(f'email_otp:{user.email.lower()}', user.email_verification_code, ttl * 60)


def set_password_reset(user):
    user.password_reset_code = generate_email_otp()
    user.password_reset_sent_at = utc_now_naive()
    ttl = int(current_app.config.get('PASSWORD_RESET_OTP_TTL_MINUTES', 10))
    user.password_reset_expires_at = user.password_reset_sent_at + timedelta(minutes=ttl)

    if redis_is_configured():
        set_otp(f'password_reset_otp:{user.email.lower()}', user.password_reset_code, ttl * 60)


def should_require_email_verification():
    return bool(current_app.config.get('EMAIL_VERIFICATION_REQUIRED', True))


def include_demo_otp_if_enabled(payload, user, email_sent):
    if email_sent:
        return payload
    if current_app.config.get('DEMO_OTP_FALLBACK', False):
        payload['demo_otp'] = user.email_verification_code
        payload['message'] = payload.get('message', 'Verification pending') + ' (Demo OTP included)'
    return payload


def normalize_phone(phone_value):
    if phone_value is None:
        return None

    raw = str(phone_value).strip()
    if not raw:
        return None

    digits_only = ''.join(ch for ch in raw if ch.isdigit())
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValueError('Phone number must contain 7 to 15 digits')

    return digits_only


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    if not data.get('name', '').strip():
        return jsonify({'error': 'Name is required'}), 400

    email = data['email'].strip().lower()

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    try:
        phone = normalize_phone(data.get('phone'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    user = User(
        name=data['name'].strip(),
        email=email,
        phone=phone,
        role='customer',
        address=data.get('address'),
        is_email_verified=not should_require_email_verification(),
    )
    user.set_password(data['password'])

    email_sent = False
    if should_require_email_verification():
        set_email_verification(user)

    db.session.add(user)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Invalid registration data'}), 400

    if should_require_email_verification():
        email_sent = send_verification_otp(user.email, user.email_verification_code)
        notify_user(
            user.id,
            title='Account Created',
            message='Your account was created. Please verify your email OTP to activate sign-in.',
            kind='account',
            entity_type='user',
            entity_id=user.id,
        )
        payload = {
            'requires_verification': True,
            'email_sent': email_sent,
            'message': 'Registration successful. Verify email to continue.',
            'user': user.to_dict(),
        }
        return jsonify(include_demo_otp_if_enabled(payload, user, email_sent)), 201

    token = create_access_token(identity=str(user.id))
    try:
        send_role_welcome_email(user)
    except Exception:
        pass
    return jsonify({'token': token, 'user': user.to_dict(), 'requires_verification': False}), 201


@auth_bp.route('/register/cook', methods=['POST'])
def register_cook():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    if not data.get('name', '').strip():
        return jsonify({'error': 'Name is required'}), 400

    email = data['email'].strip().lower()

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    try:
        phone = normalize_phone(data.get('phone'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    user = User(
        name=data['name'].strip(),
        email=email,
        phone=phone,
        role='cook',
        address=data.get('address'),
        is_email_verified=not should_require_email_verification(),
    )
    user.set_password(data['password'])

    email_sent = False
    if should_require_email_verification():
        set_email_verification(user)

    db.session.add(user)
    db.session.flush()

    cook_profile = CookProfile(
        user_id=user.id,
        specialization=data.get('specialization'),
        experience_type=data.get('experience_type'),
        years_experience=data.get('years_experience', 0),
        aadhar_number=data.get('aadhar_number'),
        bank_account=data.get('bank_account'),
        ifsc_code=data.get('ifsc_code'),
        pan_number=data.get('pan_number'),
        upi_id=data.get('upi_id'),
        payout_frequency=data.get('payout_frequency', 'weekly')
    )
    db.session.add(cook_profile)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Invalid registration data'}), 400

    if should_require_email_verification():
        email_sent = send_verification_otp(user.email, user.email_verification_code)
        notify_user(
            user.id,
            title='Cook Account Created',
            message='Your cook account was created. Please verify your email OTP to activate sign-in.',
            kind='account',
            entity_type='user',
            entity_id=user.id,
        )
        payload = {
            'requires_verification': True,
            'email_sent': email_sent,
            'message': 'Registration successful. Verify email to continue.',
            'user': user.to_dict(),
        }
        return jsonify(include_demo_otp_if_enabled(payload, user, email_sent)), 201

    token = create_access_token(identity=str(user.id))
    try:
        send_role_welcome_email(user)
    except Exception:
        pass
    return jsonify({'token': token, 'user': user.to_dict(), 'requires_verification': False}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data['email'].strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    if should_require_email_verification() and not user.is_email_verified:
        return jsonify({'error': 'Email not verified. Please verify your email first.'}), 403

    if not user.is_active:
        return jsonify({'error': 'Account deactivated'}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()})


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    otp = (data.get('otp') or '').strip()

    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.is_email_verified:
        token = create_access_token(identity=str(user.id))
        return jsonify({'message': 'Email already verified', 'token': token, 'user': user.to_dict()})

    expected_otp = None
    if redis_is_configured():
        expected_otp = get_otp(f'email_otp:{email}')

    if expected_otp is None:
        if not user.email_verification_code or not user.email_verification_expires_at:
            return jsonify({'error': 'Verification code not found. Please resend OTP.'}), 400
        if utc_now_naive() > user.email_verification_expires_at:
            return jsonify({'error': 'OTP expired. Please resend OTP.'}), 400
        expected_otp = user.email_verification_code

    if otp != expected_otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    user.is_email_verified = True
    user.email_verification_code = None
    user.email_verification_expires_at = None
    user.email_verification_sent_at = None
    db.session.commit()

    if redis_is_configured():
        delete_otp(f'email_otp:{email}')

    try:
        send_role_welcome_email(user)
    except Exception:
        pass

    token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Email verified successfully', 'token': token, 'user': user.to_dict()})


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.is_email_verified:
        return jsonify({'message': 'Email already verified'})

    set_email_verification(user)
    db.session.commit()

    email_sent = send_verification_otp(user.email, user.email_verification_code)
    payload = {'message': 'OTP resent. Please check your inbox.'}
    return jsonify(include_demo_otp_if_enabled(payload, user, email_sent))


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        set_password_reset(user)
        db.session.commit()
        try:
            send_password_reset_otp(user.email, user.password_reset_code, user.name)
        except Exception:
            pass

    # Keep response generic to avoid account enumeration.
    return jsonify({'message': 'If this email is registered, a reset OTP has been sent.'})


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    otp = (data.get('otp') or '').strip()
    new_password = (data.get('new_password') or '').strip()

    if not email or not otp or not new_password:
        return jsonify({'error': 'Email, OTP and new password are required'}), 400

    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid or expired reset OTP'}), 400

    expected_otp = None
    if redis_is_configured():
        expected_otp = get_otp(f'password_reset_otp:{email}')

    if expected_otp is None:
        if not user.password_reset_code or not user.password_reset_expires_at:
            return jsonify({'error': 'Invalid or expired reset OTP'}), 400
        if utc_now_naive() > user.password_reset_expires_at:
            return jsonify({'error': 'Reset OTP expired. Please request a new one.'}), 400
        expected_otp = user.password_reset_code

    if otp != expected_otp:
        return jsonify({'error': 'Invalid or expired reset OTP'}), 400

    user.set_password(new_password)
    user.password_reset_code = None
    user.password_reset_expires_at = None
    user.password_reset_sent_at = None
    db.session.commit()

    if redis_is_configured():
        delete_otp(f'password_reset_otp:{email}')

    return jsonify({'message': 'Password reset successful. You can now sign in.'})


@auth_bp.route('/me', methods=['GET'])
def me():
    from flask_jwt_extended import jwt_required, get_jwt_identity
    @jwt_required()
    def _inner():
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        data = user.to_dict()
        if user.role == 'cook' and user.cook_profile:
            data['cook_profile'] = user.cook_profile.to_dict()
        return jsonify(data)
    return _inner()


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    from flask_jwt_extended import jwt_required, get_jwt_identity
    @jwt_required()
    def _inner():
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        data = request.get_json()
        if not user.check_password(data.get('current_password', '')):
            return jsonify({'error': 'Current password is incorrect'}), 401
        if len(data.get('new_password', '')) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'})
    return _inner()
