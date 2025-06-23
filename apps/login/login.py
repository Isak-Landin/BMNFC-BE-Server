from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

import pytz
from apps.extensions import to_stockholm_time

from apps.manage.models import RegisteredUsers
from apps.login.models import UserLogin
from apps.extensions import db

# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.


login_blueprint = Blueprint('login_blueprint', __name__, url_prefix='/login')


# TODO: Make sure that this is client/server split compatible

@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Here we will later handle the login logic and instead of username and password we are using an NFC tag
        # Logic for managing nfc

        # For now, let's just redirect to the same login page welcoming the user
        # Todo - Implement the actual login logic with NFC and some confirmation of the user having logged in
        pass

    return render_template('login.html')


@login_blueprint.route('/nfc-scan', methods=['POST'])
def nfc_scan():
    data = request.get_json()
    tag_id = data.get('tag_id')

    if not tag_id:
        return jsonify({'status': 'error', 'message': 'Ingen tagg-ID mottagen'}), 400

    user = RegisteredUsers.query.filter_by(tag_id=tag_id).first()

    if not user:
        return jsonify({'status': 'error', 'message': 'Tagg-ID ogiltig'}), 404

    now = to_stockholm_time(datetime.now())
    if user.last_scan_time and (now - user.last_scan_time) <= timedelta(minutes=1):
        return jsonify({'status': 'wait', 'message': 'Vänligen vänta en minut innan du skannar igen'}), 429

    # Toggle login state
    user.is_logged_in = not user.is_logged_in
    user.last_scan_time = now
    db.session.commit()

    return jsonify({
        'success': True,
        'name': user.user_name,
        'new_state': 'inloggad' if user.is_logged_in else 'utloggad'
    }), 200
