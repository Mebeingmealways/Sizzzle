from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import math


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # customer, cook, manager, admin
    address = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    notification_preferences = db.Column(db.JSON, nullable=False, default=lambda: {
        'booking_confirmations': True,
        'cook_arrival_alerts': True,
        'promotional_offers': False,
    })
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_code = db.Column(db.String(6))
    email_verification_expires_at = db.Column(db.DateTime)
    email_verification_sent_at = db.Column(db.DateTime)
    password_reset_code = db.Column(db.String(6))
    password_reset_expires_at = db.Column(db.DateTime)
    password_reset_sent_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now_naive)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    # Relationships
    cook_profile = db.relationship('CookProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='customer', foreign_keys='Booking.customer_id', lazy='dynamic')
    taste_profile = db.relationship('TasteProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'notification_preferences': self.notification_preferences or {
                'booking_confirmations': True,
                'cook_arrival_alerts': True,
                'promotional_offers': False,
            },
            'is_email_verified': self.is_email_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CookProfile(db.Model):
    __tablename__ = 'cook_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(80))
    experience_type = db.Column(db.String(40))  # Home Cook, Professional Chef, Catering Expert
    years_experience = db.Column(db.Integer, default=0)
    aadhar_number = db.Column(db.String(14))
    fssai_license = db.Column(db.String(20))
    rating = db.Column(db.Float, default=0.0)
    total_jobs = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    verification_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    travel_radius_km = db.Column(db.Integer, default=10)
    availability_schedule = db.Column(db.JSON, nullable=False, default=list)
    blocked_dates = db.Column(db.JSON, nullable=False, default=list)
    bank_account = db.Column(db.String(20))
    ifsc_code = db.Column(db.String(11))
    pan_number = db.Column(db.String(10))
    upi_id = db.Column(db.String(50))
    payout_frequency = db.Column(db.String(20), default='weekly')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_accuracy_m = db.Column(db.Float)
    location_updated_at = db.Column(db.DateTime)

    # Relationships
    availability = db.relationship('CookAvailability', backref='cook', cascade='all, delete-orphan')
    dishes = db.relationship('CookDish', backref='cook', cascade='all, delete-orphan')

    def to_dict(self):
        user = self.user
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': user.name if user else None,
            'email': user.email if user else None,
            'phone': user.phone if user else None,
            'specialization': self.specialization,
            'experience_type': self.experience_type,
            'years_experience': self.years_experience,
            'rating': self.rating,
            'total_jobs': self.total_jobs,
            'total_earnings': self.total_earnings,
            'verification_status': self.verification_status,
            'travel_radius_km': self.travel_radius_km,
            'availability_schedule': self.availability_schedule or [],
            'blocked_dates': self.blocked_dates or [],
            'aadhar_number': self.aadhar_number,
            'bank_account': self.bank_account,
            'ifsc_code': self.ifsc_code,
            'upi_id': self.upi_id,
            'pan_number': self.pan_number,
            'payout_frequency': self.payout_frequency,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_accuracy_m': self.location_accuracy_m,
            'location_updated_at': self.location_updated_at.isoformat() if self.location_updated_at else None
        }

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class CookAvailability(db.Model):
    __tablename__ = 'cook_availability'

    id = db.Column(db.Integer, primary_key=True)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook_profiles.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Mon, 6=Sun
    slot = db.Column(db.String(20))  # Morning, Afternoon, Evening
    is_available = db.Column(db.Boolean, default=True)


class CookDish(db.Model):
    __tablename__ = 'cook_dishes'

    id = db.Column(db.Integer, primary_key=True)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook_profiles.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)


class Dish(db.Model):
    __tablename__ = 'dishes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(40))  # Starters, Mains, Breads, Rice, Desserts, Beverages
    cuisine = db.Column(db.String(40))
    veg_nonveg = db.Column(db.String(10), default='veg')  # veg, nonveg, egg
    description = db.Column(db.Text)
    prep_time_minutes = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'cuisine': self.cuisine,
            'veg_nonveg': self.veg_nonveg,
            'description': self.description,
            'prep_time_minutes': self.prep_time_minutes
        }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook_profiles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(10))  # HH:MM
    num_people = db.Column(db.Integer, nullable=False)
    tier = db.Column(db.String(20), default='standard')  # standard, premium
    status = db.Column(db.String(20), default='pending')  # pending, accepted, in_progress, completed, cancelled
    otp_code = db.Column(db.String(6))
    total_amount = db.Column(db.Float, default=0.0)
    platform_fee = db.Column(db.Float, default=0.0)
    cook_earnings = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    address = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    service_started_at = db.Column(db.DateTime)
    service_ended_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_charge = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=utc_now_naive)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    # Relationships
    cook_profile = db.relationship('CookProfile', backref='bookings')
    dishes = db.relationship('BookingDish', backref='booking', cascade='all, delete-orphan')
    review = db.relationship('Review', backref='booking', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        cook_user = self.cook_profile.user if self.cook_profile else None
        return {
            'id': self.id,
            'booking_code': self.booking_code,
            'customer_id': self.customer_id,
            'cook_id': self.cook_id,
            'cook_name': cook_user.name if cook_user else None,
            'cook_phone': cook_user.phone if cook_user else None,
            'date': self.date.isoformat() if self.date else None,
            'time_slot': self.time_slot,
            'num_people': self.num_people,
            'tier': self.tier,
            'status': self.status,
            'total_amount': self.total_amount,
            'cook_earnings': self.cook_earnings,
            'platform_fee': self.platform_fee,
            'otp_code': self.otp_code,
            'notes': self.notes,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'service_started_at': self.service_started_at.isoformat() if self.service_started_at else None,
            'service_ended_at': self.service_ended_at.isoformat() if self.service_ended_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_charge': self.cancellation_charge,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'dishes': [bd.dish.to_dict() for bd in self.dishes if bd.dish]
        }


class BookingDish(db.Model):
    __tablename__ = 'booking_dishes'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    dish = db.relationship('Dish')


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook_profiles.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now_naive)

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TasteProfile(db.Model):
    __tablename__ = 'taste_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    dietary_preferences = db.Column(db.JSON, default=list)  # ['Vegetarian', 'Vegan', ...]
    allergies = db.Column(db.JSON, default=list)
    spice_level = db.Column(db.Integer, default=3)  # 1-5
    kitchen_equipment = db.Column(db.JSON, default=list)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'dietary_preferences': self.dietary_preferences,
            'allergies': self.allergies,
            'spice_level': self.spice_level,
            'kitchen_equipment': self.kitchen_equipment
        }


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cook_id = db.Column(db.Integer, db.ForeignKey('cook_profiles.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(10), default='Medium')  # Low, Medium, High, Critical
    status = db.Column(db.String(20), default='Open')  # Open, Investigating, Resolved, Escalated
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolution_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now_naive)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    booking = db.relationship('Booking', backref='complaints')

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'subject': self.subject,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'manager_id': self.manager_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PlatformPolicy(db.Model):
    __tablename__ = 'platform_policies'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(60), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    unit = db.Column(db.String(20))  # grams, ml, pieces, cups
    is_mandatory = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit,
            'is_mandatory': self.is_mandatory
        }


class DishIngredient(db.Model):
    __tablename__ = 'dish_ingredients'

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity = db.Column(db.String(50))  # e.g. "500g", "2 cups"

    dish = db.relationship('Dish', backref='ingredients')
    ingredient = db.relationship('Ingredient')

    def to_dict(self):
        return {
            'ingredient': self.ingredient.to_dict() if self.ingredient else None,
            'quantity': self.quantity
        }


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(140), nullable=False)
    message = db.Column(db.Text, nullable=False)
    kind = db.Column(db.String(40), default='system')
    entity_type = db.Column(db.String(40))
    entity_id = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now_naive, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'kind': self.kind,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
