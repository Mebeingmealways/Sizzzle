from app import db
from models import Notification, User, CookProfile


def create_notification(user_id, title, message, kind='system', entity_type=None, entity_id=None):
    if not user_id or not title or not message:
        return None

    note = Notification(
        user_id=user_id,
        title=title,
        message=message,
        kind=kind,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.session.add(note)
    return note


def notify_user(user_id, title, message, kind='system', entity_type=None, entity_id=None, commit=True):
    note = create_notification(user_id, title, message, kind, entity_type, entity_id)
    if commit and note is not None:
        db.session.commit()
    return note


def notify_roles(roles, title, message, kind='system', entity_type=None, entity_id=None, commit=True):
    role_list = [r for r in (roles or []) if r]
    if not role_list:
        return []

    users = User.query.filter(User.role.in_(role_list), User.is_active.is_(True)).all()
    notes = []
    for user in users:
        note = create_notification(user.id, title, message, kind, entity_type, entity_id)
        if note is not None:
            notes.append(note)

    if commit and notes:
        db.session.commit()
    return notes


def notify_booking_parties(
    booking,
    customer_title,
    customer_message,
    cook_title,
    cook_message,
    kind='booking',
    commit=True,
):
    notes = []
    if not booking:
        return notes

    if booking.customer_id:
        note = create_notification(
            booking.customer_id,
            customer_title,
            customer_message,
            kind=kind,
            entity_type='booking',
            entity_id=booking.id,
        )
        if note is not None:
            notes.append(note)

    cook_user_id = None
    if booking.cook_profile and booking.cook_profile.user_id:
        cook_user_id = booking.cook_profile.user_id
    elif booking.cook_id:
        cook = db.session.get(CookProfile, booking.cook_id)
        cook_user_id = cook.user_id if cook else None

    if cook_user_id:
        note = create_notification(
            cook_user_id,
            cook_title,
            cook_message,
            kind=kind,
            entity_type='booking',
            entity_id=booking.id,
        )
        if note is not None:
            notes.append(note)

    if commit and notes:
        db.session.commit()
    return notes
