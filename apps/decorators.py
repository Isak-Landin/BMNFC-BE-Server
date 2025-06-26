from flask_login import current_user
from functools import wraps
from flask import redirect, url_for
from apps.manage.models import AdminUser
from flask import request, jsonify
import os

# This file is part of a proprietary system jointly owned by Isak Landin and Compliq IT AB.
# Contact either party for licensing or usage inquiries.


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('manage_blueprint.manage_login'))

        if not isinstance(current_user._get_current_object(), AdminUser):
            return redirect(url_for('manage_blueprint.manage_login'))

        return view_func(*args, **kwargs)

    return wrapped_view


def require_nfc_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        secret = os.getenv('NFC_SECRET_TOKEN')
        auth = request.headers.get('Authorization', '')
        if auth != f'Bearer {secret}':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper
