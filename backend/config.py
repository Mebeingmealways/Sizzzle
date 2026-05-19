import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _to_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _parse_origins(value):
    if not value:
        return [
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'https://sizzle.me',
            'https://www.sizzle.me',
            'https://sizzzle.me',
            'https://www.sizzzle.me',
            'https://api.sizzle.me',
            'https://api.sizzzle.me',
            'https://sizzzle.pages.dev',
        ]
    return [origin.strip() for origin in value.split(',') if origin.strip()]


def _database_uri():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # SQLAlchemy expects postgresql:// instead of deprecated postgres://.
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    return 'sqlite:///' + os.path.join(BASE_DIR, 'sizzzle.db')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sizzzle-dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'sizzzle-dev-jwt-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    CORS_ORIGINS = _parse_origins(os.environ.get('CORS_ORIGINS'))

    # Email verification (Resend)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
    RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'Sizzzle <noreply@sizzzle.me>')
    RESEND_FALLBACK_FROM_EMAIL = os.environ.get(
        'RESEND_FALLBACK_FROM_EMAIL',
        'Sizzzle <onboarding@resend.dev>',
    )
    RESEND_USER_AGENT = os.environ.get('RESEND_USER_AGENT', 'Sizzzle-Backend/1.0')
    EMAIL_BRAND_NAME = os.environ.get('EMAIL_BRAND_NAME', 'Sizzzle')
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'https://sizzzle.me')
    PUBLIC_API_BASE = os.environ.get('PUBLIC_API_BASE', 'https://api.sizzzle.me/api').rstrip('/')
    APP_LOGO_URL = os.environ.get('APP_LOGO_URL', 'https://sizzzle.me/iconlogo.png')
    EMAIL_VERIFICATION_REQUIRED = _to_bool(
        os.environ.get('EMAIL_VERIFICATION_REQUIRED'),
        default=True,
    )
    EMAIL_OTP_TTL_MINUTES = int(os.environ.get('EMAIL_OTP_TTL_MINUTES', '10'))
    PASSWORD_RESET_OTP_TTL_MINUTES = int(os.environ.get('PASSWORD_RESET_OTP_TTL_MINUTES', '10'))

    # Optional Upstash Redis (REST API) for OTP storage.
    UPSTASH_REDIS_REST_URL = os.environ.get('UPSTASH_REDIS_REST_URL', '').strip()
    UPSTASH_REDIS_REST_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN', '').strip()
    UPSTASH_REDIS_API_KEY = os.environ.get('UPSTASH_REDIS_API_KEY', '').strip()

    # Startup DB behavior (helpful for Docker demo environments like HF Spaces)
    AUTO_INIT_DB = _to_bool(os.environ.get('AUTO_INIT_DB'), default=True)
    AUTO_SEED_DEMO_DATA = _to_bool(os.environ.get('AUTO_SEED_DEMO_DATA'), default=True)
    AUTO_RESET_SQLITE_ON_SCHEMA_MISMATCH = _to_bool(
        os.environ.get('AUTO_RESET_SQLITE_ON_SCHEMA_MISMATCH'),
        default=True,
    )
    RESET_DB_ON_START = _to_bool(os.environ.get('RESET_DB_ON_START'), default=False)

    # Demo helper: when true, include OTP in responses only if email delivery fails.
    DEMO_OTP_FALLBACK = _to_bool(os.environ.get('DEMO_OTP_FALLBACK'), default=False)
