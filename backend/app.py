import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask import jsonify, Response, request
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()
jwt = JWTManager()


def _is_sqlite(app):
    return str(app.config.get('SQLALCHEMY_DATABASE_URI', '')).startswith('sqlite')


def _has_schema_mismatch(app):
    """Detect common sqlite schema drift after model updates in demo deployments."""
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = set(inspector.get_table_names())

        if 'users' not in table_names or 'cook_profiles' not in table_names:
            return True

        user_columns = {c['name'] for c in inspector.get_columns('users')}
        cook_columns = {c['name'] for c in inspector.get_columns('cook_profiles')}

        required_user = {
            'is_email_verified',
            'email_verification_code',
            'email_verification_expires_at',
            'email_verification_sent_at',
            'password_reset_code',
            'password_reset_expires_at',
            'password_reset_sent_at',
            'notification_preferences',
        }
        required_cook = {'location_accuracy_m'}

        return not required_user.issubset(user_columns) or not required_cook.issubset(cook_columns)


def _prepare_database(app):
    if not app.config.get('AUTO_INIT_DB', True):
        return

    from models import User

    if _is_sqlite(app) and app.config.get('RESET_DB_ON_START', False):
        with app.app_context():
            db.drop_all()
            db.create_all()
        return

    with app.app_context():
        db.create_all()

    if _is_sqlite(app) and app.config.get('AUTO_RESET_SQLITE_ON_SCHEMA_MISMATCH', True):
        if _has_schema_mismatch(app):
            with app.app_context():
                db.drop_all()
                db.create_all()

    if _is_sqlite(app) and app.config.get('AUTO_SEED_DEMO_DATA', True):
        try:
            with app.app_context():
                should_seed = User.query.count() == 0
        except SQLAlchemyError:
            should_seed = True

        if should_seed:
            from bootstrap_data import seed
            seed(app=app, reset=False)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', '*'),
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )
    db.init_app(app)
    jwt.init_app(app)

    from routes.auth import auth_bp
    from routes.bookings import bookings_bp
    from routes.cooks import cooks_bp
    from routes.dishes import dishes_bp
    from routes.manager import manager_bp
    from routes.admin import admin_bp
    from routes.profile import profile_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(cooks_bp, url_prefix='/api/cooks')
    app.register_blueprint(dishes_bp, url_prefix='/api/dishes')
    app.register_blueprint(manager_bp, url_prefix='/api/manager')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    _prepare_database(app)

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'app': 'Sizzzle API'}

    @app.route('/')
    def root():
        return {
            'app': 'Sizzzle API',
            'status': 'ok',
            'health': '/api/health',
            'docs': '/docs',
            'api_docs': '/api/docs',
            'project_docs': '/project-docs',
        }

    @app.route('/openapi.json')
    @app.route('/api/openapi.json')
    def openapi_json():
        public_api_base = app.config.get('PUBLIC_API_BASE', 'https://api.sizzzle.me/api').rstrip('/')
        current_api_base = f"{request.host_url.rstrip('/')}/api"

        servers = [
            {'url': public_api_base, 'description': 'Primary API domain'},
            {'url': '/api', 'description': 'Relative API base'},
            {'url': current_api_base, 'description': 'Current host API'},
        ]

        # Keep order stable but avoid duplicate server URLs.
        seen = set()
        unique_servers = []
        for server in servers:
            url = server.get('url')
            if url not in seen:
                unique_servers.append(server)
                seen.add(url)

        def schema_ref(name):
            return {'$ref': f"#/components/schemas/{name}"}

        def array_ref(name):
            return {'type': 'array', 'items': schema_ref(name)}

        def req_body(schema_name, required=True):
            return {
                'required': required,
                'content': {
                    'application/json': {
                        'schema': schema_ref(schema_name)
                    }
                }
            }

        def json_response(description, schema_name=None, schema=None):
            payload = {'description': description}
            if schema_name or schema:
                payload['content'] = {
                    'application/json': {
                        'schema': schema_ref(schema_name) if schema_name else schema
                    }
                }
            return payload

        def error_response(description):
            return json_response(description, 'ErrorResponse')

        spec = {
            'openapi': '3.0.3',
            'info': {
                'title': 'Sizzzle API',
                'version': '1.1.0',
                'description': (
                    'Structured REST API for the Sizzzle home-cooking platform. '\
                    'Supports customer bookings, cook operations, manager workflows, '\
                    'admin governance, preferences, notifications, and analytics.'
                ),
            },
            'externalDocs': {
                'description': 'Complete backend + frontend + DB system documentation',
                'url': '/project-docs',
            },
            'tags': [
                {'name': 'Authentication', 'description': 'Registration, login, email OTP, and password lifecycle.'},
                {'name': 'Bookings', 'description': 'Booking creation and workflow state transitions.'},
                {'name': 'Cooks', 'description': 'Cook directory, recommendation, availability, jobs, earnings, and location.'},
                {'name': 'Dishes', 'description': 'Dish catalog and ingredient aggregation for meal preparation.'},
                {'name': 'Manager', 'description': 'Verification queue, complaints, and cook monitoring.'},
                {'name': 'Admin', 'description': 'Platform governance, policy control, managers, disputes, and analytics.'},
                {'name': 'Profile', 'description': 'User profile, taste preferences, and kitchen readiness.'},
                {'name': 'Notifications', 'description': 'In-app notification retrieval and read status management.'},
                {'name': 'System', 'description': 'Health and service metadata endpoints.'},
            ],
            'servers': unique_servers,
            'components': {
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT',
                    }
                },
                'parameters': {
                    'PathId': {
                        'name': 'id',
                        'in': 'path',
                        'required': True,
                        'description': 'Resource identifier.',
                        'schema': {'type': 'integer'}
                    },
                    'BookingStatusQuery': {
                        'name': 'status',
                        'in': 'query',
                        'required': False,
                        'description': 'Filter bookings by status.',
                        'schema': {
                            'type': 'string',
                            'enum': ['pending', 'accepted', 'in_progress', 'completed', 'cancelled']
                        }
                    },
                    'DishCategoryQuery': {
                        'name': 'category',
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'string'},
                        'description': 'Filter dishes by category.'
                    },
                    'DishCuisineQuery': {
                        'name': 'cuisine',
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'string'},
                        'description': 'Filter dishes by cuisine.'
                    },
                    'SearchQuery': {
                        'name': 'search',
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'string'},
                        'description': 'Search query text.'
                    },
                    'PeriodQuery': {
                        'name': 'period',
                        'in': 'query',
                        'required': False,
                        'description': 'Analytics lookback period like 30d.',
                        'schema': {'type': 'string', 'example': '30d'}
                    },
                    'LimitQuery': {
                        'name': 'limit',
                        'in': 'query',
                        'required': False,
                        'description': 'Max number of records to return (1-100).',
                        'schema': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 20}
                    },
                    'UnreadOnlyQuery': {
                        'name': 'unread_only',
                        'in': 'query',
                        'required': False,
                        'description': 'When true, only unread notifications are returned.',
                        'schema': {'type': 'boolean', 'default': False}
                    }
                },
                'schemas': {
                    'ErrorResponse': {
                        'type': 'object',
                        'properties': {'error': {'type': 'string'}},
                        'required': ['error']
                    },
                    'MessageResponse': {
                        'type': 'object',
                        'properties': {'message': {'type': 'string'}},
                        'required': ['message']
                    },
                    'HealthResponse': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string', 'example': 'ok'},
                            'app': {'type': 'string', 'example': 'Sizzzle API'}
                        },
                        'required': ['status', 'app']
                    },
                    'User': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'},
                            'phone': {'type': 'string', 'nullable': True},
                            'role': {'type': 'string', 'enum': ['customer', 'cook', 'manager', 'admin']},
                            'address': {'type': 'string', 'nullable': True},
                            'latitude': {'type': 'number', 'nullable': True},
                            'longitude': {'type': 'number', 'nullable': True},
                            'is_email_verified': {'type': 'boolean'},
                            'is_active': {'type': 'boolean'},
                            'created_at': {'type': 'string', 'format': 'date-time', 'nullable': True}
                        },
                        'required': ['id', 'name', 'email', 'role']
                    },
                    'CookProfile': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'user_id': {'type': 'integer'},
                            'name': {'type': 'string', 'nullable': True},
                            'email': {'type': 'string', 'nullable': True},
                            'phone': {'type': 'string', 'nullable': True},
                            'specialization': {'type': 'string', 'nullable': True},
                            'experience_type': {'type': 'string', 'nullable': True},
                            'years_experience': {'type': 'integer'},
                            'rating': {'type': 'number'},
                            'total_jobs': {'type': 'integer'},
                            'total_earnings': {'type': 'number'},
                            'verification_status': {'type': 'string', 'enum': ['pending', 'approved', 'rejected']},
                            'travel_radius_km': {'type': 'integer'},
                            'latitude': {'type': 'number', 'nullable': True},
                            'longitude': {'type': 'number', 'nullable': True},
                            'location_accuracy_m': {'type': 'number', 'nullable': True},
                            'location_updated_at': {'type': 'string', 'format': 'date-time', 'nullable': True}
                        },
                        'required': ['id', 'user_id', 'verification_status']
                    },
                    'Dish': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'category': {'type': 'string', 'nullable': True},
                            'cuisine': {'type': 'string', 'nullable': True},
                            'veg_nonveg': {'type': 'string', 'nullable': True},
                            'description': {'type': 'string', 'nullable': True},
                            'prep_time_minutes': {'type': 'integer', 'nullable': True}
                        },
                        'required': ['id', 'name']
                    },
                    'IngredientItem': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'unit': {'type': 'string', 'nullable': True},
                            'quantity': {'type': 'string', 'nullable': True},
                            'is_mandatory': {'type': 'boolean'}
                        },
                        'required': ['name']
                    },
                    'Booking': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'booking_code': {'type': 'string'},
                            'customer_id': {'type': 'integer'},
                            'cook_id': {'type': 'integer'},
                            'cook_name': {'type': 'string', 'nullable': True},
                            'cook_phone': {'type': 'string', 'nullable': True},
                            'date': {'type': 'string', 'format': 'date'},
                            'time_slot': {'type': 'string', 'nullable': True},
                            'num_people': {'type': 'integer'},
                            'tier': {'type': 'string', 'enum': ['standard', 'premium']},
                            'status': {'type': 'string', 'enum': ['pending', 'accepted', 'in_progress', 'completed', 'cancelled']},
                            'total_amount': {'type': 'number'},
                            'cook_earnings': {'type': 'number'},
                            'platform_fee': {'type': 'number'},
                            'otp_code': {'type': 'string', 'nullable': True},
                            'notes': {'type': 'string', 'nullable': True},
                            'address': {'type': 'string', 'nullable': True},
                            'latitude': {'type': 'number', 'nullable': True},
                            'longitude': {'type': 'number', 'nullable': True},
                            'service_started_at': {'type': 'string', 'format': 'date-time', 'nullable': True},
                            'service_ended_at': {'type': 'string', 'format': 'date-time', 'nullable': True},
                            'cancelled_at': {'type': 'string', 'format': 'date-time', 'nullable': True},
                            'cancellation_charge': {'type': 'number'},
                            'created_at': {'type': 'string', 'format': 'date-time', 'nullable': True},
                            'dishes': array_ref('Dish')
                        },
                        'required': ['id', 'booking_code', 'customer_id', 'cook_id', 'status']
                    },
                    'Review': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'booking_id': {'type': 'integer'},
                            'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                            'comment': {'type': 'string', 'nullable': True},
                            'created_at': {'type': 'string', 'format': 'date-time', 'nullable': True}
                        },
                        'required': ['id', 'booking_id', 'rating']
                    },
                    'Complaint': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'booking_id': {'type': 'integer'},
                            'subject': {'type': 'string'},
                            'description': {'type': 'string', 'nullable': True},
                            'priority': {'type': 'string', 'enum': ['Low', 'Medium', 'High', 'Critical']},
                            'status': {'type': 'string', 'enum': ['Open', 'Investigating', 'Resolved', 'Escalated']},
                            'manager_id': {'type': 'integer', 'nullable': True},
                            'created_at': {'type': 'string', 'format': 'date-time', 'nullable': True}
                        },
                        'required': ['id', 'booking_id', 'subject', 'status']
                    },
                    'PlatformPolicy': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'key': {'type': 'string'},
                            'value': {'type': 'string'},
                            'description': {'type': 'string', 'nullable': True}
                        },
                        'required': ['id', 'key', 'value']
                    },
                    'TasteProfile': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'nullable': True},
                            'user_id': {'type': 'integer', 'nullable': True},
                            'dietary_preferences': {'type': 'array', 'items': {'type': 'string'}},
                            'allergies': {'type': 'array', 'items': {'type': 'string'}},
                            'spice_level': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                            'kitchen_equipment': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    },
                    'Notification': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'user_id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'message': {'type': 'string'},
                            'kind': {'type': 'string'},
                            'entity_type': {'type': 'string', 'nullable': True},
                            'entity_id': {'type': 'integer', 'nullable': True},
                            'is_read': {'type': 'boolean'},
                            'created_at': {'type': 'string', 'format': 'date-time', 'nullable': True}
                        },
                        'required': ['id', 'title', 'message', 'is_read']
                    },
                    'AuthTokenResponse': {
                        'type': 'object',
                        'properties': {
                            'token': {'type': 'string'},
                            'user': schema_ref('User')
                        },
                        'required': ['token', 'user']
                    },
                    'AuthRegistrationResponse': {
                        'type': 'object',
                        'properties': {
                            'token': {'type': 'string', 'nullable': True},
                            'requires_verification': {'type': 'boolean'},
                            'email_sent': {'type': 'boolean', 'nullable': True},
                            'message': {'type': 'string', 'nullable': True},
                            'user': schema_ref('User')
                        },
                        'required': ['user']
                    },
                    'UserProfileResponse': {
                        'type': 'object',
                        'allOf': [
                            schema_ref('User'),
                            {
                                'type': 'object',
                                'properties': {
                                    'cook_profile': schema_ref('CookProfile'),
                                    'taste_profile': schema_ref('TasteProfile')
                                }
                            }
                        ]
                    },
                    'CookLocationResponse': {
                        'type': 'object',
                        'properties': {
                            'latitude': {'type': 'number', 'nullable': True},
                            'longitude': {'type': 'number', 'nullable': True},
                            'accuracy_m': {'type': 'number', 'nullable': True},
                            'updated_at': {'type': 'string', 'format': 'date-time', 'nullable': True}
                        }
                    },
                    'OtpVerificationResponse': {
                        'type': 'object',
                        'properties': {
                            'verified': {'type': 'boolean'},
                            'booking': schema_ref('Booking')
                        },
                        'required': ['verified']
                    },
                    'CancelBookingResponse': {
                        'type': 'object',
                        'properties': {
                            'booking': schema_ref('Booking'),
                            'cancellation_charge': {'type': 'number'},
                            'message': {'type': 'string'}
                        },
                        'required': ['booking', 'cancellation_charge', 'message']
                    },
                    'CookDetailResponse': {
                        'type': 'object',
                        'allOf': [
                            schema_ref('CookProfile'),
                            {
                                'type': 'object',
                                'properties': {
                                    'availability': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'day': {'type': 'integer'},
                                                'slot': {'type': 'string', 'nullable': True},
                                                'available': {'type': 'boolean'}
                                            }
                                        }
                                    },
                                    'dishes': array_ref('Dish')
                                }
                            }
                        ]
                    },
                    'RecommendedCook': {
                        'type': 'object',
                        'allOf': [
                            schema_ref('CookProfile'),
                            {
                                'type': 'object',
                                'properties': {
                                    'match_score': {'type': 'number'},
                                    'distance_km': {'type': 'number', 'nullable': True}
                                }
                            }
                        ]
                    },
                    'EarningsSnapshot': {
                        'type': 'object',
                        'properties': {
                            'total_earned': {'type': 'number'},
                            'total_bookings': {'type': 'integer'},
                            'average_per_job': {'type': 'number'},
                            'rating': {'type': 'number'},
                            'weekly_earnings': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'day': {'type': 'string'},
                                        'date': {'type': 'string', 'format': 'date'},
                                        'amount': {'type': 'number'}
                                    }
                                }
                            },
                            'payouts': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'date': {'type': 'string', 'format': 'date'},
                                        'amount': {'type': 'number'},
                                        'booking_code': {'type': 'string'},
                                        'status': {'type': 'string'}
                                    }
                                }
                            },
                            'payout_frequency': {'type': 'string'}
                        },
                        'required': ['total_earned', 'total_bookings']
                    },
                    'VerificationPayload': {'type': 'object', 'additionalProperties': True},
                    'ManagerVerificationActionResponse': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'reason': {'type': 'string', 'nullable': True},
                            'cook': schema_ref('VerificationPayload')
                        },
                        'required': ['message', 'cook']
                    },
                    'AdminStatsResponse': {
                        'type': 'object',
                        'properties': {
                            'total_users': {'type': 'integer'},
                            'total_cooks': {'type': 'integer'},
                            'total_bookings': {'type': 'integer'},
                            'total_revenue': {'type': 'number'},
                            'open_disputes': {'type': 'integer'},
                            'completed_bookings': {'type': 'integer'},
                            'cancelled_bookings': {'type': 'integer'}
                        },
                        'required': ['total_users', 'total_cooks', 'total_bookings', 'total_revenue']
                    },
                    'AnalyticsSnapshot': {'type': 'object', 'additionalProperties': True},
                    'KitchenChecklistResponse': {
                        'type': 'object',
                        'properties': {
                            'kitchen_equipment': {'type': 'array', 'items': {'type': 'string'}}
                        },
                        'required': ['kitchen_equipment']
                    },
                    'NotificationListResponse': {
                        'type': 'object',
                        'properties': {
                            'items': array_ref('Notification'),
                            'unread_count': {'type': 'integer'}
                        },
                        'required': ['items', 'unread_count']
                    },
                    'UnreadCountResponse': {
                        'type': 'object',
                        'properties': {'unread_count': {'type': 'integer'}},
                        'required': ['unread_count']
                    },
                    'MarkReadResponse': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'notification': schema_ref('Notification')
                        },
                        'required': ['message', 'notification']
                    },
                    'RegisterCustomerRequest': {
                        'type': 'object',
                        'required': ['name', 'email', 'password'],
                        'properties': {
                            'name': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'},
                            'password': {'type': 'string', 'minLength': 6},
                            'phone': {'type': 'string'},
                            'address': {'type': 'string'}
                        }
                    },
                    'RegisterCookRequest': {
                        'type': 'object',
                        'required': ['name', 'email', 'password'],
                        'properties': {
                            'name': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'},
                            'password': {'type': 'string', 'minLength': 6},
                            'phone': {'type': 'string'},
                            'address': {'type': 'string'},
                            'specialization': {'type': 'string'},
                            'experience_type': {'type': 'string'},
                            'years_experience': {'type': 'integer', 'minimum': 0},
                            'aadhar_number': {'type': 'string'},
                            'bank_account': {'type': 'string'},
                            'ifsc_code': {'type': 'string'},
                            'pan_number': {'type': 'string'},
                            'upi_id': {'type': 'string'},
                            'payout_frequency': {'type': 'string', 'enum': ['daily', 'weekly', 'monthly']}
                        }
                    },
                    'LoginRequest': {
                        'type': 'object',
                        'required': ['email', 'password'],
                        'properties': {
                            'email': {'type': 'string', 'format': 'email'},
                            'password': {'type': 'string'}
                        }
                    },
                    'EmailOtpRequest': {
                        'type': 'object',
                        'required': ['email', 'otp'],
                        'properties': {
                            'email': {'type': 'string', 'format': 'email'},
                            'otp': {'type': 'string', 'minLength': 4, 'maxLength': 6}
                        }
                    },
                    'EmailRequest': {
                        'type': 'object',
                        'required': ['email'],
                        'properties': {'email': {'type': 'string', 'format': 'email'}}
                    },
                    'ResetPasswordRequest': {
                        'type': 'object',
                        'required': ['email', 'otp', 'new_password'],
                        'properties': {
                            'email': {'type': 'string', 'format': 'email'},
                            'otp': {'type': 'string', 'minLength': 4, 'maxLength': 6},
                            'new_password': {'type': 'string', 'minLength': 8}
                        }
                    },
                    'ChangePasswordRequest': {
                        'type': 'object',
                        'required': ['current_password', 'new_password'],
                        'properties': {
                            'current_password': {'type': 'string'},
                            'new_password': {'type': 'string', 'minLength': 6}
                        }
                    },
                    'CreateBookingRequest': {
                        'type': 'object',
                        'required': ['cook_id', 'date'],
                        'properties': {
                            'cook_id': {'type': 'integer'},
                            'date': {'type': 'string', 'format': 'date'},
                            'time_slot': {'type': 'string', 'example': '19:00'},
                            'num_people': {'type': 'integer', 'minimum': 1},
                            'tier': {'type': 'string', 'enum': ['standard', 'premium']},
                            'total_amount': {'type': 'number', 'minimum': 0},
                            'notes': {'type': 'string'},
                            'address': {'type': 'string'},
                            'latitude': {'type': 'number'},
                            'longitude': {'type': 'number'},
                            'dish_ids': {'type': 'array', 'items': {'type': 'integer'}}
                        }
                    },
                    'UpdateBookingStatusRequest': {
                        'type': 'object',
                        'required': ['status'],
                        'properties': {
                            'status': {'type': 'string', 'enum': ['accepted', 'in_progress', 'completed', 'cancelled']}
                        }
                    },
                    'OtpVerifyRequest': {
                        'type': 'object',
                        'required': ['otp'],
                        'properties': {'otp': {'type': 'string', 'minLength': 4, 'maxLength': 6}}
                    },
                    'RatingRequest': {
                        'type': 'object',
                        'required': ['rating'],
                        'properties': {
                            'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                            'comment': {'type': 'string'}
                        }
                    },
                    'AvailabilityUpdateRequest': {
                        'type': 'object',
                        'properties': {
                            'slots': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'required': ['day'],
                                    'properties': {
                                        'day': {'type': 'integer', 'minimum': 0, 'maximum': 6},
                                        'slot': {'type': 'string'},
                                        'available': {'type': 'boolean'}
                                    }
                                }
                            },
                            'travel_radius_km': {'type': 'integer', 'minimum': 1}
                        }
                    },
                    'CookRecommendationRequest': {
                        'type': 'object',
                        'properties': {
                            'latitude': {'type': 'number'},
                            'longitude': {'type': 'number'}
                        }
                    },
                    'CookLocationUpdateRequest': {
                        'type': 'object',
                        'required': ['latitude', 'longitude'],
                        'properties': {
                            'latitude': {'type': 'number', 'minimum': -90, 'maximum': 90},
                            'longitude': {'type': 'number', 'minimum': -180, 'maximum': 180},
                            'accuracy_m': {'type': 'number', 'minimum': 0, 'maximum': 5000}
                        }
                    },
                    'DishIngredientsRequest': {
                        'type': 'object',
                        'required': ['dish_ids'],
                        'properties': {
                            'dish_ids': {'type': 'array', 'items': {'type': 'integer'}}
                        }
                    },
                    'ManagerVerificationActionRequest': {
                        'type': 'object',
                        'required': ['action'],
                        'properties': {
                            'action': {'type': 'string', 'enum': ['approve', 'reject', 'send_for_verification']},
                            'reason': {'type': 'string', 'nullable': True}
                        }
                    },
                    'LegacyVerificationUpdateRequest': {
                        'type': 'object',
                        'required': ['status'],
                        'properties': {
                            'status': {'type': 'string', 'enum': ['approved', 'rejected']}
                        }
                    },
                    'CreateComplaintRequest': {
                        'type': 'object',
                        'required': ['booking_id', 'subject'],
                        'properties': {
                            'booking_id': {'type': 'integer'},
                            'subject': {'type': 'string'},
                            'description': {'type': 'string'},
                            'priority': {'type': 'string', 'enum': ['Low', 'Medium', 'High', 'Critical']}
                        }
                    },
                    'UpdateComplaintRequest': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'resolution_notes': {'type': 'string'}
                        }
                    },
                    'ResolveComplaintRequest': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'resolution_notes': {'type': 'string'}
                        }
                    },
                    'CreateManagerRequest': {
                        'type': 'object',
                        'required': ['email', 'password'],
                        'properties': {
                            'name': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'},
                            'password': {'type': 'string', 'minLength': 6},
                            'phone': {'type': 'string'},
                            'region': {'type': 'string'}
                        }
                    },
                    'AssignRegionRequest': {
                        'type': 'object',
                        'properties': {
                            'region': {'type': 'string'}
                        }
                    },
                    'UpdatePoliciesRequest': {
                        'type': 'object',
                        'required': ['policies'],
                        'properties': {
                            'policies': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'required': ['key', 'value'],
                                    'properties': {
                                        'key': {'type': 'string'},
                                        'value': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    },
                    'UpdatePolicyRequest': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string'},
                            'description': {'type': 'string'}
                        }
                    },
                    'ProfileUpdateRequest': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'address': {'type': 'string'},
                            'latitude': {'type': 'number'},
                            'longitude': {'type': 'number'}
                        }
                    },
                    'TasteProfileUpdateRequest': {
                        'type': 'object',
                        'properties': {
                            'dietary_preferences': {'type': 'array', 'items': {'type': 'string'}},
                            'allergies': {'type': 'array', 'items': {'type': 'string'}},
                            'spice_level': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                            'kitchen_equipment': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    },
                    'KitchenChecklistRequest': {
                        'type': 'object',
                        'required': ['kitchen_equipment'],
                        'properties': {
                            'kitchen_equipment': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    }
                }
            },
            'paths': {
                '/auth/register': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Register customer account',
                        'description': 'Creates a customer account. Public registration always maps role to customer.',
                        'security': [],
                        'requestBody': req_body('RegisterCustomerRequest'),
                        'responses': {
                            '201': json_response('Customer account created', 'AuthRegistrationResponse'),
                            '400': error_response('Validation failed'),
                            '409': error_response('Email already registered')
                        }
                    }
                },
                '/auth/register/cook': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Register cook account',
                        'description': 'Creates a cook user and cook profile with verification fields.',
                        'security': [],
                        'requestBody': req_body('RegisterCookRequest'),
                        'responses': {
                            '201': json_response('Cook account created', 'AuthRegistrationResponse'),
                            '400': error_response('Validation failed'),
                            '409': error_response('Email already registered')
                        }
                    }
                },
                '/auth/login': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Login user',
                        'security': [],
                        'requestBody': req_body('LoginRequest'),
                        'responses': {
                            '200': json_response('Login success', 'AuthTokenResponse'),
                            '400': error_response('Email/password required'),
                            '401': error_response('Invalid credentials'),
                            '403': error_response('Email not verified or account deactivated')
                        }
                    }
                },
                '/auth/me': {
                    'get': {
                        'tags': ['Authentication'],
                        'summary': 'Get current user profile',
                        'responses': {
                            '200': json_response('Current user profile', 'UserProfileResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/auth/change-password': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Change authenticated user password',
                        'requestBody': req_body('ChangePasswordRequest'),
                        'responses': {
                            '200': json_response('Password updated', 'MessageResponse'),
                            '400': error_response('Validation failed'),
                            '401': error_response('Current password invalid'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/auth/verify-email': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Verify email OTP',
                        'security': [],
                        'requestBody': req_body('EmailOtpRequest'),
                        'responses': {
                            '200': json_response('Email verification successful', 'AuthTokenResponse'),
                            '400': error_response('Invalid or expired OTP'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/auth/resend-otp': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Resend verification OTP',
                        'security': [],
                        'requestBody': req_body('EmailRequest'),
                        'responses': {
                            '200': json_response('OTP resent', 'MessageResponse'),
                            '400': error_response('Email required'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/auth/forgot-password': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Send password reset OTP',
                        'security': [],
                        'requestBody': req_body('EmailRequest'),
                        'responses': {
                            '200': json_response('OTP dispatch response', 'MessageResponse'),
                            '400': error_response('Email required')
                        }
                    }
                },
                '/auth/reset-password': {
                    'post': {
                        'tags': ['Authentication'],
                        'summary': 'Reset password using OTP',
                        'security': [],
                        'requestBody': req_body('ResetPasswordRequest'),
                        'responses': {
                            '200': json_response('Password reset success', 'MessageResponse'),
                            '400': error_response('Invalid payload or OTP')
                        }
                    }
                },
                '/bookings': {
                    'get': {
                        'tags': ['Bookings'],
                        'summary': 'List bookings by role scope',
                        'parameters': [{'$ref': '#/components/parameters/BookingStatusQuery'}],
                        'responses': {
                            '200': json_response('Bookings list', schema=array_ref('Booking')),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User or cook profile not found')
                        }
                    },
                    'post': {
                        'tags': ['Bookings'],
                        'summary': 'Create a booking',
                        'description': 'Requires at least 1 day advance date. Tier supports standard/premium.',
                        'requestBody': req_body('CreateBookingRequest'),
                        'responses': {
                            '201': json_response('Booking created', 'Booking'),
                            '400': error_response('Validation failed'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Cook unavailable or not found')
                        }
                    }
                },
                '/bookings/{id}': {
                    'get': {
                        'tags': ['Bookings'],
                        'summary': 'Get booking details',
                        'responses': {
                            '200': json_response('Booking detail', 'Booking'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/bookings/{id}/status': {
                    'patch': {
                        'tags': ['Bookings'],
                        'summary': 'Update booking status via valid transition',
                        'requestBody': req_body('UpdateBookingStatusRequest'),
                        'responses': {
                            '200': json_response('Booking updated', 'Booking'),
                            '400': error_response('Invalid state transition'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/bookings/{id}/cancel': {
                    'post': {
                        'tags': ['Bookings'],
                        'summary': 'Cancel a booking',
                        'description': 'Cancellation charge rules: >12h = 0%, 12-6h = 50%, <6h = 80%.',
                        'responses': {
                            '200': json_response('Booking cancelled', 'CancelBookingResponse'),
                            '400': error_response('Booking cannot be cancelled'),
                            '401': error_response('Missing or invalid token'),
                            '403': error_response('Unauthorized cancellation attempt'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/bookings/{id}/verify-otp': {
                    'post': {
                        'tags': ['Bookings'],
                        'summary': 'Verify service start OTP',
                        'requestBody': req_body('OtpVerifyRequest'),
                        'responses': {
                            '200': json_response('OTP verification result', 'OtpVerificationResponse'),
                            '400': error_response('Invalid OTP'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/bookings/{id}/start': {
                    'post': {
                        'tags': ['Bookings'],
                        'summary': 'Mark booking as in progress',
                        'responses': {
                            '200': json_response('Service started', 'Booking'),
                            '400': error_response('Booking is not in accepted state'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/bookings/{id}/end': {
                    'post': {
                        'tags': ['Bookings'],
                        'summary': 'Mark booking as completed',
                        'responses': {
                            '200': json_response('Service ended', 'Booking'),
                            '400': error_response('Booking is not in progress'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/bookings/{id}/rate': {
                    'post': {
                        'tags': ['Bookings'],
                        'summary': 'Rate completed booking',
                        'requestBody': req_body('RatingRequest'),
                        'responses': {
                            '201': json_response('Review created', 'Review'),
                            '400': error_response('Invalid rating or booking state'),
                            '401': error_response('Missing or invalid token'),
                            '403': error_response('Only customer can rate'),
                            '404': error_response('Booking not found'),
                            '409': error_response('Already rated')
                        }
                    }
                },
                '/bookings/{id}/cook-location': {
                    'get': {
                        'tags': ['Bookings'],
                        'summary': 'Get live cook location for active booking',
                        'responses': {
                            '200': json_response('Cook location', 'CookLocationResponse'),
                            '400': error_response('Booking is not active for location sharing'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/cooks': {
                    'get': {
                        'tags': ['Cooks'],
                        'summary': 'List cooks',
                        'parameters': [
                            {
                                'name': 'status',
                                'in': 'query',
                                'required': False,
                                'schema': {'type': 'string', 'default': 'approved'},
                                'description': 'Verification status filter.'
                            },
                            {
                                'name': 'specialization',
                                'in': 'query',
                                'required': False,
                                'schema': {'type': 'string'},
                                'description': 'Cook specialization filter.'
                            }
                        ],
                        'responses': {
                            '200': json_response('Cook list', schema=array_ref('CookProfile'))
                        }
                    }
                },
                '/cooks/{id}': {
                    'get': {
                        'tags': ['Cooks'],
                        'summary': 'Get cook details',
                        'responses': {
                            '200': json_response('Cook details', 'CookDetailResponse'),
                            '404': error_response('Cook not found')
                        }
                    }
                },
                '/cooks/recommend': {
                    'post': {
                        'tags': ['Cooks'],
                        'summary': 'Recommend cooks with match score (0-100)',
                        'description': 'Weighted score: Distance 30, Quality 30, Verification 20, Personalization 20.',
                        'requestBody': req_body('CookRecommendationRequest', required=False),
                        'responses': {
                            '200': json_response('Recommended cooks', schema=array_ref('RecommendedCook')),
                            '401': error_response('Missing or invalid token')
                        }
                    }
                },
                '/cooks/recommended': {
                    'get': {
                        'tags': ['Cooks'],
                        'summary': 'Get top rated approved cooks',
                        'responses': {
                            '200': json_response('Top cooks', schema=array_ref('CookProfile')),
                            '401': error_response('Missing or invalid token')
                        }
                    }
                },
                '/cooks/{id}/availability': {
                    'put': {
                        'tags': ['Cooks'],
                        'summary': 'Update availability by cook id',
                        'requestBody': req_body('AvailabilityUpdateRequest'),
                        'responses': {
                            '200': json_response('Availability updated', 'MessageResponse'),
                            '401': error_response('Missing or invalid token'),
                            '403': error_response('Unauthorized'),
                            '404': error_response('Cook not found')
                        }
                    }
                },
                '/cooks/availability': {
                    'put': {
                        'tags': ['Cooks'],
                        'summary': 'Update own cook availability',
                        'requestBody': req_body('AvailabilityUpdateRequest'),
                        'responses': {
                            '200': json_response('Availability updated', 'MessageResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Cook profile not found')
                        }
                    }
                },
                '/cooks/earnings': {
                    'get': {
                        'tags': ['Cooks'],
                        'summary': 'Get cook earnings dashboard data',
                        'responses': {
                            '200': json_response('Earnings snapshot', 'EarningsSnapshot'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Cook profile not found')
                        }
                    }
                },
                '/cooks/jobs': {
                    'get': {
                        'tags': ['Cooks'],
                        'summary': 'Get cook jobs',
                        'parameters': [{'$ref': '#/components/parameters/BookingStatusQuery'}],
                        'responses': {
                            '200': json_response('Cook jobs', schema=array_ref('Booking')),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Cook profile not found')
                        }
                    }
                },
                '/cooks/location': {
                    'post': {
                        'tags': ['Cooks'],
                        'summary': 'Update cook live location',
                        'requestBody': req_body('CookLocationUpdateRequest'),
                        'responses': {
                            '200': json_response('Location updated', 'CookLocationResponse'),
                            '400': error_response('Invalid location payload'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Cook profile not found')
                        }
                    }
                },
                '/dishes': {
                    'get': {
                        'tags': ['Dishes'],
                        'summary': 'List active dishes',
                        'parameters': [
                            {'$ref': '#/components/parameters/DishCategoryQuery'},
                            {'$ref': '#/components/parameters/DishCuisineQuery'},
                            {'$ref': '#/components/parameters/SearchQuery'}
                        ],
                        'responses': {
                            '200': json_response('Dish list', schema=array_ref('Dish'))
                        }
                    }
                },
                '/dishes/{id}': {
                    'get': {
                        'tags': ['Dishes'],
                        'summary': 'Get dish details with ingredients',
                        'responses': {
                            '200': json_response(
                                'Dish details',
                                schema={
                                    'allOf': [
                                        schema_ref('Dish'),
                                        {
                                            'type': 'object',
                                            'properties': {
                                                'ingredients': {
                                                    'type': 'array',
                                                    'items': {'type': 'object', 'additionalProperties': True}
                                                }
                                            }
                                        }
                                    ]
                                }
                            ),
                            '404': error_response('Dish not found')
                        }
                    }
                },
                '/dishes/ingredients': {
                    'post': {
                        'tags': ['Dishes'],
                        'summary': 'Get merged ingredient list for selected dishes',
                        'requestBody': req_body('DishIngredientsRequest'),
                        'responses': {
                            '200': json_response('Merged ingredient list', schema=array_ref('IngredientItem')),
                            '400': error_response('Invalid request body')
                        }
                    }
                },
                '/manager/verification-queue': {
                    'get': {
                        'tags': ['Manager'],
                        'summary': 'Get cook verification queue',
                        'parameters': [
                            {
                                'name': 'status',
                                'in': 'query',
                                'required': False,
                                'schema': {'type': 'string', 'default': 'pending'}
                            }
                        ],
                        'responses': {
                            '200': json_response('Verification queue', schema=array_ref('VerificationPayload')),
                            '403': error_response('Manager access required')
                        }
                    }
                },
                '/manager/verifications/pending': {
                    'get': {
                        'tags': ['Manager'],
                        'summary': 'Get pending verification submissions',
                        'responses': {
                            '200': json_response('Pending verifications', schema=array_ref('VerificationPayload')),
                            '403': error_response('Manager access required')
                        }
                    }
                },
                '/manager/verifications/{id}': {
                    'get': {
                        'tags': ['Manager'],
                        'summary': 'Get verification details for one cook',
                        'responses': {
                            '200': json_response('Verification details', 'VerificationPayload'),
                            '403': error_response('Manager access required'),
                            '404': error_response('Cook not found')
                        }
                    },
                    'post': {
                        'tags': ['Manager'],
                        'summary': 'Approve, reject, or send cook for verification',
                        'requestBody': req_body('ManagerVerificationActionRequest'),
                        'responses': {
                            '200': json_response('Verification action applied', 'ManagerVerificationActionResponse'),
                            '400': error_response('Invalid action'),
                            '403': error_response('Manager access required'),
                            '404': error_response('Cook not found')
                        }
                    }
                },
                '/manager/verify/{id}': {
                    'patch': {
                        'tags': ['Manager'],
                        'summary': 'Legacy verification status update',
                        'requestBody': req_body('LegacyVerificationUpdateRequest'),
                        'responses': {
                            '200': json_response('Verification status updated', 'VerificationPayload'),
                            '400': error_response('Invalid status value'),
                            '403': error_response('Manager access required'),
                            '404': error_response('Cook not found')
                        }
                    }
                },
                '/manager/complaints': {
                    'get': {
                        'tags': ['Manager'],
                        'summary': 'List complaints',
                        'parameters': [
                            {
                                'name': 'status',
                                'in': 'query',
                                'required': False,
                                'schema': {'type': 'string'}
                            }
                        ],
                        'responses': {
                            '200': json_response('Complaints list', schema=array_ref('Complaint')),
                            '403': error_response('Manager access required')
                        }
                    },
                    'post': {
                        'tags': ['Manager'],
                        'summary': 'Create complaint',
                        'requestBody': req_body('CreateComplaintRequest'),
                        'responses': {
                            '201': json_response('Complaint created', 'Complaint'),
                            '400': error_response('Required fields missing'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Booking not found')
                        }
                    }
                },
                '/manager/complaints/{id}': {
                    'patch': {
                        'tags': ['Manager'],
                        'summary': 'Update complaint status and notes',
                        'requestBody': req_body('UpdateComplaintRequest'),
                        'responses': {
                            '200': json_response('Complaint updated', 'Complaint'),
                            '403': error_response('Manager access required'),
                            '404': error_response('Complaint not found')
                        }
                    }
                },
                '/manager/complaints/{id}/resolve': {
                    'post': {
                        'tags': ['Manager'],
                        'summary': 'Resolve complaint',
                        'requestBody': req_body('ResolveComplaintRequest', required=False),
                        'responses': {
                            '200': json_response('Complaint resolved', 'Complaint'),
                            '403': error_response('Manager access required'),
                            '404': error_response('Complaint not found')
                        }
                    }
                },
                '/manager/cook-metrics': {
                    'get': {
                        'tags': ['Manager'],
                        'summary': 'Get per-cook performance metrics',
                        'responses': {
                            '200': json_response('Cook metrics', schema={'type': 'array', 'items': {'type': 'object', 'additionalProperties': True}}),
                            '403': error_response('Manager access required')
                        }
                    }
                },
                '/manager/cooks': {
                    'get': {
                        'tags': ['Manager'],
                        'summary': 'List manager-visible approved cooks',
                        'responses': {
                            '200': json_response('Managed cooks', schema=array_ref('CookProfile')),
                            '403': error_response('Manager access required')
                        }
                    }
                },
                '/admin/stats': {
                    'get': {
                        'tags': ['Admin'],
                        'summary': 'Get platform KPI stats',
                        'responses': {
                            '200': json_response('Admin stats', 'AdminStatsResponse'),
                            '403': error_response('Admin access required')
                        }
                    }
                },
                '/admin/analytics': {
                    'get': {
                        'tags': ['Admin'],
                        'summary': 'Get analytics snapshot with trends and growth',
                        'parameters': [{'$ref': '#/components/parameters/PeriodQuery'}],
                        'responses': {
                            '200': json_response('Analytics snapshot', 'AnalyticsSnapshot'),
                            '403': error_response('Admin access required')
                        }
                    }
                },
                '/admin/managers': {
                    'get': {
                        'tags': ['Admin'],
                        'summary': 'List managers',
                        'responses': {
                            '200': json_response('Manager list', schema=array_ref('User')),
                            '403': error_response('Admin access required')
                        }
                    },
                    'post': {
                        'tags': ['Admin'],
                        'summary': 'Create manager account',
                        'requestBody': req_body('CreateManagerRequest'),
                        'responses': {
                            '201': json_response('Manager created', 'User'),
                            '400': error_response('Validation failed'),
                            '403': error_response('Admin access required'),
                            '409': error_response('Email already registered')
                        }
                    }
                },
                '/admin/managers/{id}/region': {
                    'post': {
                        'tags': ['Admin'],
                        'summary': 'Assign manager region',
                        'requestBody': req_body('AssignRegionRequest', required=False),
                        'responses': {
                            '200': json_response('Manager updated', 'User'),
                            '400': error_response('User is not a manager'),
                            '403': error_response('Admin access required'),
                            '404': error_response('Manager not found')
                        }
                    }
                },
                '/admin/policies': {
                    'get': {
                        'tags': ['Admin'],
                        'summary': 'List platform policies',
                        'responses': {
                            '200': json_response('Policies', schema=array_ref('PlatformPolicy')),
                            '403': error_response('Admin access required')
                        }
                    },
                    'put': {
                        'tags': ['Admin'],
                        'summary': 'Bulk update platform policies',
                        'requestBody': req_body('UpdatePoliciesRequest'),
                        'responses': {
                            '200': json_response('Policies updated', 'MessageResponse'),
                            '403': error_response('Admin access required')
                        }
                    }
                },
                '/admin/policies/{id}': {
                    'put': {
                        'tags': ['Admin'],
                        'summary': 'Update one platform policy',
                        'requestBody': req_body('UpdatePolicyRequest'),
                        'responses': {
                            '200': json_response('Policy updated', 'PlatformPolicy'),
                            '403': error_response('Admin access required'),
                            '404': error_response('Policy not found')
                        }
                    }
                },
                '/admin/disputes': {
                    'get': {
                        'tags': ['Admin'],
                        'summary': 'List unresolved disputes',
                        'responses': {
                            '200': json_response('Dispute list', schema=array_ref('Complaint')),
                            '403': error_response('Admin access required')
                        }
                    }
                },
                '/admin/disputes/{id}': {
                    'patch': {
                        'tags': ['Admin'],
                        'summary': 'Patch dispute resolution status',
                        'requestBody': req_body('ResolveComplaintRequest', required=False),
                        'responses': {
                            '200': json_response('Dispute updated', 'Complaint'),
                            '403': error_response('Admin access required'),
                            '404': error_response('Dispute not found')
                        }
                    }
                },
                '/admin/disputes/{id}/resolve': {
                    'post': {
                        'tags': ['Admin'],
                        'summary': 'Resolve dispute using action endpoint',
                        'requestBody': req_body('ResolveComplaintRequest', required=False),
                        'responses': {
                            '200': json_response('Dispute resolved', 'Complaint'),
                            '403': error_response('Admin access required'),
                            '404': error_response('Dispute not found')
                        }
                    }
                },
                '/profile': {
                    'get': {
                        'tags': ['Profile'],
                        'summary': 'Get own profile',
                        'responses': {
                            '200': json_response('Profile', 'UserProfileResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User not found')
                        }
                    },
                    'put': {
                        'tags': ['Profile'],
                        'summary': 'Update own profile basics',
                        'requestBody': req_body('ProfileUpdateRequest', required=False),
                        'responses': {
                            '200': json_response('Profile updated', 'User'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/profile/change-password': {
                    'post': {
                        'tags': ['Profile'],
                        'summary': 'Change password from profile settings',
                        'requestBody': req_body('ChangePasswordRequest'),
                        'responses': {
                            '200': json_response('Password updated', 'MessageResponse'),
                            '400': error_response('Validation failed'),
                            '401': error_response('Invalid current password or token'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/profile/taste': {
                    'get': {
                        'tags': ['Profile'],
                        'summary': 'Get taste profile',
                        'responses': {
                            '200': json_response('Taste profile', 'TasteProfile'),
                            '401': error_response('Missing or invalid token')
                        }
                    },
                    'put': {
                        'tags': ['Profile'],
                        'summary': 'Update taste profile and kitchen preferences',
                        'requestBody': req_body('TasteProfileUpdateRequest', required=False),
                        'responses': {
                            '200': json_response('Taste profile updated', 'TasteProfile'),
                            '401': error_response('Missing or invalid token')
                        }
                    }
                },
                '/profile/kitchen-checklist': {
                    'get': {
                        'tags': ['Profile'],
                        'summary': 'Get kitchen equipment checklist',
                        'responses': {
                            '200': json_response('Kitchen checklist', 'KitchenChecklistResponse'),
                            '401': error_response('Missing or invalid token')
                        }
                    },
                    'put': {
                        'tags': ['Profile'],
                        'summary': 'Update kitchen equipment checklist',
                        'requestBody': req_body('KitchenChecklistRequest'),
                        'responses': {
                            '200': json_response('Kitchen checklist updated', 'KitchenChecklistResponse'),
                            '401': error_response('Missing or invalid token')
                        }
                    }
                },
                '/notifications': {
                    'get': {
                        'tags': ['Notifications'],
                        'summary': 'List notifications for current user',
                        'parameters': [
                            {'$ref': '#/components/parameters/LimitQuery'},
                            {'$ref': '#/components/parameters/UnreadOnlyQuery'}
                        ],
                        'responses': {
                            '200': json_response('Notifications list', 'NotificationListResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/notifications/unread-count': {
                    'get': {
                        'tags': ['Notifications'],
                        'summary': 'Get unread notifications count',
                        'responses': {
                            '200': json_response('Unread count', 'UnreadCountResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/notifications/{id}/read': {
                    'post': {
                        'tags': ['Notifications'],
                        'summary': 'Mark a notification as read',
                        'responses': {
                            '200': json_response('Notification marked as read', 'MarkReadResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('Notification or user not found')
                        }
                    }
                },
                '/notifications/read-all': {
                    'post': {
                        'tags': ['Notifications'],
                        'summary': 'Mark all notifications as read',
                        'responses': {
                            '200': json_response('All notifications marked as read', 'MessageResponse'),
                            '401': error_response('Missing or invalid token'),
                            '404': error_response('User not found')
                        }
                    }
                },
                '/health': {
                    'get': {
                        'tags': ['System'],
                        'summary': 'Health check',
                        'security': [],
                        'responses': {
                            '200': json_response('Service health', 'HealthResponse')
                        }
                    }
                }
            }
        }

        for path, operations in spec['paths'].items():
            if '{id}' in path:
                for operation in operations.values():
                    params = operation.setdefault('parameters', [])
                    has_id_param = any(
                        (p.get('$ref') == '#/components/parameters/PathId')
                        or (p.get('in') == 'path' and p.get('name') == 'id')
                        for p in params
                    )
                    if not has_id_param:
                        params.insert(0, {'$ref': '#/components/parameters/PathId'})

        protected_prefixes = (
            '/bookings',
            '/manager',
            '/admin',
            '/profile',
            '/notifications',
        )

        for path, operations in spec['paths'].items():
            requires_auth = (
                path == '/auth/me'
                or path == '/auth/change-password'
                or path == '/cooks/recommend'
                or path == '/cooks/recommended'
                or path == '/cooks/{id}/availability'
                or path == '/cooks/availability'
                or path == '/cooks/earnings'
                or path == '/cooks/jobs'
                or path == '/cooks/location'
                or path.startswith(protected_prefixes)
            )

            if requires_auth:
                for operation in operations.values():
                    operation.setdefault('security', [{'bearerAuth': []}])

        def schema_example(schema):
            schema_examples = {
                'ErrorResponse': {'error': 'Validation failed'},
                'MessageResponse': {'message': 'Operation completed successfully'},
                'HealthResponse': {'status': 'ok', 'app': 'Sizzzle API'},
                'User': {
                    'id': 12,
                    'name': 'Aarav Mehta',
                    'email': 'aarav@sizzzle.me',
                    'phone': '+91-9000000001',
                    'role': 'customer',
                    'address': 'Koramangala, Bengaluru',
                    'latitude': 12.9352,
                    'longitude': 77.6245,
                    'is_email_verified': True,
                    'is_active': True,
                    'created_at': '2026-04-15T09:40:00Z'
                },
                'CookProfile': {
                    'id': 8,
                    'user_id': 21,
                    'name': 'Chef Nisha',
                    'email': 'nisha@sizzzle.me',
                    'phone': '+91-9000000002',
                    'specialization': 'South Indian',
                    'experience_type': 'home_chef',
                    'years_experience': 6,
                    'rating': 4.8,
                    'total_jobs': 118,
                    'total_earnings': 154000.0,
                    'verification_status': 'approved',
                    'travel_radius_km': 10,
                    'latitude': 12.9716,
                    'longitude': 77.5946,
                    'location_accuracy_m': 24.5,
                    'location_updated_at': '2026-04-15T10:10:00Z'
                },
                'Dish': {
                    'id': 101,
                    'name': 'Paneer Butter Masala',
                    'category': 'Main Course',
                    'cuisine': 'North Indian',
                    'veg_nonveg': 'veg',
                    'description': 'Rich and creamy paneer curry',
                    'prep_time_minutes': 35
                },
                'IngredientItem': {
                    'name': 'Paneer',
                    'unit': 'grams',
                    'quantity': '250',
                    'is_mandatory': True
                },
                'Booking': {
                    'id': 77,
                    'booking_code': 'SZL-20260415-077',
                    'customer_id': 12,
                    'cook_id': 21,
                    'cook_name': 'Chef Nisha',
                    'cook_phone': '+91-9000000002',
                    'date': '2026-04-20',
                    'time_slot': '19:00',
                    'num_people': 4,
                    'tier': 'premium',
                    'status': 'accepted',
                    'total_amount': 2200.0,
                    'cook_earnings': 1760.0,
                    'platform_fee': 440.0,
                    'otp_code': '4821',
                    'notes': 'Less spicy preferred',
                    'address': 'HSR Layout, Bengaluru',
                    'latitude': 12.9116,
                    'longitude': 77.6412,
                    'service_started_at': None,
                    'service_ended_at': None,
                    'cancelled_at': None,
                    'cancellation_charge': 0.0,
                    'created_at': '2026-04-15T10:20:00Z',
                    'dishes': [
                        {
                            'id': 101,
                            'name': 'Paneer Butter Masala',
                            'category': 'Main Course',
                            'cuisine': 'North Indian',
                            'veg_nonveg': 'veg',
                            'description': 'Rich and creamy paneer curry',
                            'prep_time_minutes': 35
                        }
                    ]
                },
                'Review': {
                    'id': 9,
                    'booking_id': 77,
                    'rating': 5,
                    'comment': 'Excellent service and taste',
                    'created_at': '2026-04-20T21:45:00Z'
                },
                'Complaint': {
                    'id': 31,
                    'booking_id': 77,
                    'subject': 'Late arrival',
                    'description': 'Cook arrived 25 minutes late',
                    'priority': 'Medium',
                    'status': 'Open',
                    'manager_id': 4,
                    'created_at': '2026-04-20T19:30:00Z'
                },
                'PlatformPolicy': {
                    'id': 3,
                    'key': 'cancellation_charge_percent',
                    'value': '20',
                    'description': 'Charge applied for late cancellations'
                },
                'TasteProfile': {
                    'id': 12,
                    'user_id': 12,
                    'dietary_preferences': ['vegetarian'],
                    'allergies': ['peanut'],
                    'spice_level': 3,
                    'kitchen_equipment': ['pressure_cooker', 'oven']
                },
                'Notification': {
                    'id': 91,
                    'user_id': 12,
                    'title': 'Booking confirmed',
                    'message': 'Chef Nisha accepted your booking',
                    'kind': 'booking_status',
                    'entity_type': 'booking',
                    'entity_id': 77,
                    'is_read': False,
                    'created_at': '2026-04-15T10:25:00Z'
                },
                'AuthTokenResponse': {
                    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sample.signature',
                    'user': {
                        'id': 12,
                        'name': 'Aarav Mehta',
                        'email': 'aarav@sizzzle.me',
                        'phone': '+91-9000000001',
                        'role': 'customer',
                        'address': 'Koramangala, Bengaluru',
                        'latitude': 12.9352,
                        'longitude': 77.6245,
                        'is_email_verified': True,
                        'is_active': True,
                        'created_at': '2026-04-15T09:40:00Z'
                    }
                },
                'AuthRegistrationResponse': {
                    'token': None,
                    'requires_verification': True,
                    'email_sent': True,
                    'message': 'Verification OTP sent to email',
                    'user': {
                        'id': 12,
                        'name': 'Aarav Mehta',
                        'email': 'aarav@sizzzle.me',
                        'phone': '+91-9000000001',
                        'role': 'customer',
                        'address': 'Koramangala, Bengaluru',
                        'latitude': 12.9352,
                        'longitude': 77.6245,
                        'is_email_verified': False,
                        'is_active': True,
                        'created_at': '2026-04-15T09:40:00Z'
                    }
                },
                'UserProfileResponse': {
                    'id': 12,
                    'name': 'Aarav Mehta',
                    'email': 'aarav@sizzzle.me',
                    'phone': '+91-9000000001',
                    'role': 'customer',
                    'address': 'Koramangala, Bengaluru',
                    'latitude': 12.9352,
                    'longitude': 77.6245,
                    'is_email_verified': True,
                    'is_active': True,
                    'created_at': '2026-04-15T09:40:00Z',
                    'cook_profile': None,
                    'taste_profile': {
                        'id': 12,
                        'user_id': 12,
                        'dietary_preferences': ['vegetarian'],
                        'allergies': ['peanut'],
                        'spice_level': 3,
                        'kitchen_equipment': ['pressure_cooker', 'oven']
                    }
                },
                'CookLocationResponse': {
                    'latitude': 12.9716,
                    'longitude': 77.5946,
                    'accuracy_m': 14.0,
                    'updated_at': '2026-04-15T10:28:00Z'
                },
                'OtpVerificationResponse': {
                    'verified': True,
                    'booking': {
                        'id': 77,
                        'booking_code': 'SZL-20260415-077',
                        'customer_id': 12,
                        'cook_id': 21,
                        'status': 'in_progress'
                    }
                },
                'CancelBookingResponse': {
                    'booking': {
                        'id': 77,
                        'booking_code': 'SZL-20260415-077',
                        'customer_id': 12,
                        'cook_id': 21,
                        'status': 'cancelled'
                    },
                    'cancellation_charge': 440.0,
                    'message': 'Booking cancelled successfully'
                },
                'CookDetailResponse': {
                    'id': 8,
                    'user_id': 21,
                    'name': 'Chef Nisha',
                    'email': 'nisha@sizzzle.me',
                    'phone': '+91-9000000002',
                    'specialization': 'South Indian',
                    'experience_type': 'home_chef',
                    'years_experience': 6,
                    'rating': 4.8,
                    'total_jobs': 118,
                    'total_earnings': 154000.0,
                    'verification_status': 'approved',
                    'travel_radius_km': 10,
                    'latitude': 12.9716,
                    'longitude': 77.5946,
                    'location_accuracy_m': 24.5,
                    'location_updated_at': '2026-04-15T10:10:00Z',
                    'availability': [
                        {'day': 1, 'slot': '09:00-13:00', 'available': True}
                    ],
                    'dishes': [
                        {
                            'id': 101,
                            'name': 'Paneer Butter Masala',
                            'category': 'Main Course',
                            'cuisine': 'North Indian',
                            'veg_nonveg': 'veg',
                            'description': 'Rich and creamy paneer curry',
                            'prep_time_minutes': 35
                        }
                    ]
                },
                'RecommendedCook': {
                    'id': 8,
                    'user_id': 21,
                    'name': 'Chef Nisha',
                    'email': 'nisha@sizzzle.me',
                    'phone': '+91-9000000002',
                    'specialization': 'South Indian',
                    'experience_type': 'home_chef',
                    'years_experience': 6,
                    'rating': 4.8,
                    'total_jobs': 118,
                    'total_earnings': 154000.0,
                    'verification_status': 'approved',
                    'travel_radius_km': 10,
                    'latitude': 12.9716,
                    'longitude': 77.5946,
                    'location_accuracy_m': 24.5,
                    'location_updated_at': '2026-04-15T10:10:00Z',
                    'match_score': 0.93,
                    'distance_km': 2.4
                },
                'EarningsSnapshot': {
                    'total_earned': 154000.0,
                    'total_bookings': 118,
                    'average_per_job': 1305.08,
                    'rating': 4.8,
                    'weekly_earnings': [
                        {'day': 'Mon', 'date': '2026-04-13', 'amount': 3800.0}
                    ],
                    'payouts': [
                        {'id': 501, 'date': '2026-04-14', 'amount': 7600.0, 'booking_code': 'SZL-20260414-052', 'status': 'paid'}
                    ],
                    'payout_frequency': 'weekly'
                },
                'VerificationPayload': {
                    'id': 8,
                    'verification_status': 'approved'
                },
                'ManagerVerificationActionResponse': {
                    'message': 'Verification status updated',
                    'reason': None,
                    'cook': {'id': 8, 'verification_status': 'approved'}
                },
                'AdminStatsResponse': {
                    'total_users': 1200,
                    'total_cooks': 340,
                    'total_bookings': 8600,
                    'total_revenue': 12500000.0,
                    'open_disputes': 9,
                    'completed_bookings': 7920,
                    'cancelled_bookings': 680
                },
                'AnalyticsSnapshot': {
                    'period': '30d',
                    'active_users': 842,
                    'booking_growth_percent': 14.6
                },
                'KitchenChecklistResponse': {
                    'kitchen_equipment': ['gas_stove', 'pressure_cooker', 'mixie']
                },
                'NotificationListResponse': {
                    'items': [
                        {
                            'id': 91,
                            'user_id': 12,
                            'title': 'Booking confirmed',
                            'message': 'Chef Nisha accepted your booking',
                            'kind': 'booking_status',
                            'entity_type': 'booking',
                            'entity_id': 77,
                            'is_read': False,
                            'created_at': '2026-04-15T10:25:00Z'
                        }
                    ],
                    'unread_count': 3
                },
                'UnreadCountResponse': {'unread_count': 3},
                'MarkReadResponse': {
                    'message': 'Notification marked as read',
                    'notification': {
                        'id': 91,
                        'user_id': 12,
                        'title': 'Booking confirmed',
                        'message': 'Chef Nisha accepted your booking',
                        'kind': 'booking_status',
                        'entity_type': 'booking',
                        'entity_id': 77,
                        'is_read': True,
                        'created_at': '2026-04-15T10:25:00Z'
                    }
                }
            }

            if not isinstance(schema, dict):
                return {'message': 'Operation completed successfully'}

            ref = schema.get('$ref')
            if ref:
                schema_name = ref.rsplit('/', 1)[-1]
                return schema_examples.get(schema_name, {'message': 'Operation completed successfully'})

            if 'allOf' in schema:
                merged = {}
                for part in schema.get('allOf', []):
                    part_value = schema_example(part)
                    if isinstance(part_value, dict):
                        merged.update(part_value)
                return merged or {'message': 'Operation completed successfully'}

            schema_type = schema.get('type')
            if schema_type == 'array':
                item = schema_example(schema.get('items', {}))
                return [item]

            if schema_type == 'object' or 'properties' in schema:
                obj = {}
                for key, prop in schema.get('properties', {}).items():
                    if 'example' in prop:
                        obj[key] = prop['example']
                        continue
                    if '$ref' in prop:
                        obj[key] = schema_example(prop)
                        continue
                    prop_type = prop.get('type')
                    if prop_type == 'string':
                        enum_values = prop.get('enum')
                        fmt = prop.get('format')
                        if enum_values:
                            obj[key] = enum_values[0]
                        elif fmt == 'date-time':
                            obj[key] = '2026-04-15T10:30:00Z'
                        elif fmt == 'date':
                            obj[key] = '2026-04-20'
                        elif fmt == 'email':
                            obj[key] = 'sample@sizzzle.me'
                        else:
                            obj[key] = f'sample_{key}'
                    elif prop_type == 'integer':
                        obj[key] = 1
                    elif prop_type == 'number':
                        obj[key] = 1.0
                    elif prop_type == 'boolean':
                        obj[key] = True
                    elif prop_type == 'array':
                        obj[key] = [schema_example(prop.get('items', {}))]
                    elif prop_type == 'object':
                        obj[key] = {}
                    else:
                        obj[key] = None
                return obj or {'message': 'Operation completed successfully'}

            return {'message': 'Operation completed successfully'}

        status_examples = {
            '400': {'error': 'Validation failed: please check request payload and parameters'},
            '401': {'error': 'Unauthorized: missing or invalid bearer token'},
            '403': {'error': 'Forbidden: you do not have permission to perform this action'},
            '404': {'error': 'Not found: requested resource does not exist'},
            '409': {'error': 'Conflict: resource already exists or state conflict detected'},
        }

        for operations in spec['paths'].values():
            for operation in operations.values():
                responses = operation.get('responses', {})
                for status_code, response in responses.items():
                    content = response.get('content', {})
                    app_json = content.get('application/json')
                    if not app_json:
                        continue

                    code = str(status_code)
                    schema = app_json.get('schema')

                    if code in status_examples:
                        app_json['example'] = status_examples[code]
                    elif code.startswith('2') and schema:
                        app_json['example'] = schema_example(schema)
                    elif schema:
                        app_json['example'] = {'error': response.get('description', 'Request failed')}

        return jsonify(spec)

    @app.route('/project-docs')
    @app.route('/api/project-docs')
    def project_docs():
        docs_path = os.path.join(os.path.dirname(__file__), 'project_docs.html')
        try:
            with open(docs_path, 'r', encoding='utf-8') as file_obj:
                return Response(file_obj.read(), mimetype='text/html')
        except OSError:
            return jsonify({'error': 'Project documentation file not found'}), 404

    @app.route('/docs')
    @app.route('/api/docs')
    def docs():
        html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sizzzle API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({
    url: window.location.pathname.startsWith('/api') ? '/api/openapi.json' : '/openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
            persistAuthorization: true,
    });
  </script>
</body>
</html>
"""
        return Response(html, mimetype='text/html')

    return app
