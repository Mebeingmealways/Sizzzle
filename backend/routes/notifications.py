from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Notification, User, db

notifications_bp = Blueprint('notifications', __name__)


def _current_user():
    user_id = int(get_jwt_identity())
    return db.session.get(User, user_id)


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    limit = request.args.get('limit', '20')
    try:
        limit = max(1, min(int(limit), 100))
    except (TypeError, ValueError):
        limit = 20

    unread_only = str(request.args.get('unread_only', 'false')).strip().lower() in ('1', 'true', 'yes')

    query = Notification.query.filter_by(user_id=user.id)
    if unread_only:
        query = query.filter_by(is_read=False)

    items = query.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(limit).all()
    unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()

    return jsonify({
        'items': [item.to_dict() for item in items],
        'unread_count': unread_count,
    })


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    return jsonify({'unread_count': count})


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_read(notification_id):
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    note = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not note:
        return jsonify({'error': 'Notification not found'}), 404

    if not note.is_read:
        note.is_read = True
        db.session.commit()

    return jsonify({'message': 'Notification marked as read', 'notification': note.to_dict()})


@notifications_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_read():
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'})
