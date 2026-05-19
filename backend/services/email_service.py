import html
import json
import urllib.error
import urllib.request
from datetime import datetime

from flask import current_app


ROLE_WELCOME_COPY = {
    'customer': {
        'heading': 'Welcome to Sizzzle, your home-cook marketplace.',
        'cta': 'Browse Home Cooks',
        'points': [
            'Discover verified cooks for everyday meals and special occasions.',
            'Book quickly, track your booking, and enjoy real home-made food.',
            'Manage your profile and preferences for better recommendations.',
        ],
    },
    'cook': {
        'heading': 'Welcome to Sizzzle, your kitchen business starts now.',
        'cta': 'Open Cook Dashboard',
        'points': [
            'Set your availability, menu preferences, and service areas.',
            'Manage bookings and track your completed jobs and earnings.',
            'Grow your profile with great service and consistent quality.',
        ],
    },
    'manager': {
        'heading': 'Welcome to Sizzzle management operations.',
        'cta': 'Open Manager Dashboard',
        'points': [
            'Review verification queues and monitor active operations.',
            'Resolve complaints quickly with transparent actions.',
            'Keep quality standards high across cooks and bookings.',
        ],
    },
    'admin': {
        'heading': 'Welcome to Sizzzle platform administration.',
        'cta': 'Open Admin Dashboard',
        'points': [
            'Monitor platform analytics, disputes, and performance metrics.',
            'Manage managers, policies, and operational controls.',
            'Steer platform quality, growth, and trust.',
        ],
    },
}


def _build_senders():
    from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Sizzzle <noreply@sizzzle.me>')
    fallback_from_email = current_app.config.get('RESEND_FALLBACK_FROM_EMAIL', 'Sizzzle <onboarding@resend.dev>')

    senders = []
    if from_email:
        senders.append(from_email)
    if fallback_from_email and fallback_from_email not in senders:
        senders.append(fallback_from_email)
    return senders


def _send_resend_email(to_email, subject, html_body, text_body=None):
    """Send a single email through Resend with sender fallback.

    Returns True on accepted request, False if key is missing or all sender attempts fail.
    """
    api_key = (current_app.config.get('RESEND_API_KEY') or '').strip()
    if not api_key:
        return False

    payload = {
        'to': [to_email],
        'subject': subject,
        'html': html_body,
    }
    if text_body:
        payload['text'] = text_body

    for sender in _build_senders():
        sender_payload = dict(payload)
        sender_payload['from'] = sender

        req = urllib.request.Request(
            'https://api.resend.com/emails',
            data=json.dumps(sender_payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': current_app.config.get('RESEND_USER_AGENT', 'Sizzzle-Backend/1.0'),
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                if 200 <= resp.status < 300:
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            continue

    return False


def _email_shell(title, body_html, cta_label=None, cta_url=None):
    logo_url = current_app.config.get('APP_LOGO_URL', 'https://sizzzle.me/iconlogo.png')
    brand_name = current_app.config.get('EMAIL_BRAND_NAME', 'Sizzzle')
    current_year = datetime.utcnow().year
    cta_html = ''
    if cta_label and cta_url:
        cta_html = (
            f'<p style="margin:24px 0 0 0">'
            f'<a href="{html.escape(cta_url)}" '
            'style="display:inline-block;background:#2db67d;color:#ffffff;text-decoration:none;'
            'padding:12px 18px;border-radius:10px;font-weight:700">'
            f'{html.escape(cta_label)}'
            '</a>'
            '</p>'
        )

    return (
        '<!doctype html>'
        '<html>'
        '<body style="margin:0;background:#f8faf9;padding:28px 12px;font-family:Inter,Segoe UI,Arial,sans-serif;color:#1f2937">'
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="max-width:620px;margin:0 auto">'
        '<tr><td style="padding:0">'
        '<div style="background:#ffffff;border:1px solid #e5ebe9;border-radius:16px;overflow:hidden">'
        '<div style="background:linear-gradient(90deg,#2db67d,#f2734f);height:6px"></div>'
        '<div style="padding:22px 22px 10px 22px;display:flex;align-items:center;gap:12px">'
        f'<img src="{html.escape(logo_url)}" alt="{html.escape(brand_name)}" width="44" height="44" '
        'style="border-radius:10px;border:1px solid #e8efec;display:block" />'
        f'<div style="font-size:18px;font-weight:800;color:#0f172a">{html.escape(brand_name)}</div>'
        '</div>'
        '<div style="padding:0 22px 24px 22px">'
        f'<h2 style="margin:8px 0 14px 0;font-size:24px;line-height:1.25;color:#0f172a">{html.escape(title)}</h2>'
        f'{body_html}'
        f'{cta_html}'
        '</div>'
        '<div style="padding:14px 22px 18px 22px;border-top:1px solid #edf2f0;color:#64748b;font-size:12px">'
        f'© {current_year} {html.escape(brand_name)}. Home Cooks. Real Taste.'
        '</div>'
        '</div>'
        '</td></tr>'
        '</table>'
        '</body>'
        '</html>'
    )


def send_verification_otp(email, otp_code):
    otp_safe = html.escape(str(otp_code))
    body_html = (
        '<p style="margin:0 0 12px 0;font-size:15px;line-height:1.6">'
        'Use this verification code to complete your Sizzzle sign in:'
        '</p>'
        f'<div style="font-size:34px;font-weight:800;letter-spacing:8px;color:#f2734f;'
        'background:#fff7f3;border:1px solid #fde5d8;border-radius:12px;padding:14px 16px;'
        'display:inline-block">'
        f'{otp_safe}'
        '</div>'
        '<p style="margin:14px 0 0 0;font-size:14px;line-height:1.6;color:#475569">'
        'This code expires soon. If you did not request this, you can safely ignore this email.'
        '</p>'
    )

    html_email = _email_shell('Email Verification', body_html)
    text_email = (
        f'Your Sizzzle verification code is {otp_code}. '
        'This code expires soon. If you did not request this, you can ignore this email.'
    )
    return _send_resend_email(email, 'Your Sizzzle verification code', html_email, text_email)


def send_password_reset_otp(email, otp_code, name='there'):
    otp_safe = html.escape(str(otp_code))
    safe_name = html.escape((name or 'there').strip() or 'there')
    body_html = (
        f'<p style="margin:0 0 12px 0;font-size:15px;line-height:1.6">Hi {safe_name},</p>'
        '<p style="margin:0 0 12px 0;font-size:15px;line-height:1.6">'
        'Use this one-time code to reset your Sizzzle password:'
        '</p>'
        f'<div style="font-size:34px;font-weight:800;letter-spacing:8px;color:#f2734f;'
        'background:#fff7f3;border:1px solid #fde5d8;border-radius:12px;padding:14px 16px;'
        'display:inline-block">'
        f'{otp_safe}'
        '</div>'
        '<p style="margin:14px 0 0 0;font-size:14px;line-height:1.6;color:#475569">'
        'This reset code expires soon. If you did not request a password reset, please ignore this email.'
        '</p>'
    )
    html_email = _email_shell('Reset Your Password', body_html)
    text_email = (
        f'Hi {name or "there"}, your Sizzzle password reset code is {otp_code}. '
        'This code expires soon. If you did not request this, ignore this email.'
    )
    return _send_resend_email(email, 'Your Sizzzle password reset code', html_email, text_email)


def send_role_welcome_email(user):
    if not user or not getattr(user, 'email', None):
        return False

    role = (getattr(user, 'role', 'customer') or 'customer').lower()
    copy = ROLE_WELCOME_COPY.get(role, ROLE_WELCOME_COPY['customer'])

    app_base = (current_app.config.get('APP_BASE_URL') or 'https://sizzzle.me').rstrip('/')
    dashboard_paths = {
        'customer': '/customer',
        'cook': '/cook',
        'manager': '/manager',
        'admin': '/admin',
    }
    dashboard_url = f"{app_base}{dashboard_paths.get(role, '/customer')}"

    plain_name = (getattr(user, 'name', '') or 'there').strip() or 'there'
    safe_name = html.escape(plain_name)
    role_label = html.escape(role.capitalize())
    points_html = ''.join(
        f'<li style="margin:0 0 8px 0">{html.escape(point)}</li>' for point in copy['points']
    )
    body_html = (
        f'<p style="margin:0 0 10px 0;font-size:15px;line-height:1.6">Hi {safe_name},</p>'
        f'<p style="margin:0 0 12px 0;font-size:15px;line-height:1.6">{html.escape(copy["heading"])}</p>'
        f'<p style="margin:0 0 8px 0;font-size:13px;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Account Type: {role_label}</p>'
        f'<ul style="margin:12px 0 0 18px;padding:0;font-size:14px;line-height:1.6;color:#334155">{points_html}</ul>'
    )

    subject = f'Welcome to Sizzzle, {plain_name}!'
    html_email = _email_shell(subject, body_html, copy['cta'], dashboard_url)
    text_email = (
        f'Hi {getattr(user, "name", "there")}, welcome to Sizzzle as a {role}. '
        f'Open your dashboard: {dashboard_url}'
    )
    return _send_resend_email(user.email, subject, html_email, text_email)
