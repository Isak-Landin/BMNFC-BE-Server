from flask import Blueprint, render_template, request, jsonify, current_app, stream_with_context, Response
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from apps.manage.models import RegisteredUsers
from apps.nfc.models import NFCScanBuffer
from apps.extensions import to_stockholm_time, db
from apps.nfc.models import NFCLoginLog

from apps.decorators import require_nfc_token
import json


# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.


nfc_backend_blueprint = Blueprint('nfc_backend_blueprint', __name__, url_prefix='/nfc/backend')


# TODO: Make sure that this is client/server split compatible

global register_or_login_value
register_or_login_value: str = "login"  # Default value, can be set to "register" or "login"


def internal_set_register_or_login_value(value):
    """
    Internal function to set the global register_or_login_value.
    This is used to determine if the NFC tag should go through registration or login.
    """
    global register_or_login_value
    register_or_login_value = value


NFC_SECRET_TOKEN = os.getenv('NFC_SECRET_TOKEN', default='default_token')


@nfc_backend_blueprint.route('/', methods=['GET'])
def nfc_backend():
    """
    This endpoint serves the NFC backend page.
    It renders the nfc_backend.html template.
    """
    return render_template('nfc_backend.html')


@nfc_backend_blueprint.route('/set-nfc-status', methods=['POST'])
@require_nfc_token
def set_nfc_status():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'Ingen data mottagen'}), 400

            value = data.get('value')
            if not value or value not in ['register', 'login']:
                return jsonify({'status': 'error', 'message': 'Ogiltigt värde, måste vara "register" eller "login"'}), 400

            internal_set_register_or_login_value(value)

        return jsonify({
            'status': 'success',
            'message': f'Register or login value set to {register_or_login_value}',
            'value': register_or_login_value
        }), 200

    except Exception as ex:
        current_app.logger.error(f"Unhandled exception: {ex}")
        return jsonify({'status': 'error', 'message': 'Internt serverfel'}), 500


@nfc_backend_blueprint.route('/get-nfc-status', methods=['GET'])
@require_nfc_token
def get_nfc_status():
    """
    This endpoint is used to check if the NFC tag should go through registration or login.
    It returns a simple message indicating the action to be taken.
    """
    try:

        # Here we simply return the value of register_or_login_value
        value_to_return = register_or_login_value
        internal_set_register_or_login_value("login")

        return jsonify({
            'status': 'success',
            'message': f'Tag should go through {value_to_return}',
            'value': value_to_return
        }), 200


    except Exception as ex:
        current_app.logger.error(f"Unhandled exception: {ex}")
        return jsonify({'status': 'error', 'message': 'Internt serverfel'}), 500


@nfc_backend_blueprint.route('/scan-login', methods=['POST'])
@require_nfc_token
def scan_login():
    """
    self.uid = uid
    self.message = message
    self.success = success
    self.source = source
    self.user_name = user_name
    self.created_at = to_stockholm_time(datetime.now())
    self.is_processed = is_processed
    """
    try:

        whoami = request.headers.get('whoami')
        if not whoami:
            return jsonify({'status': 'error', 'message': 'Identifier header saknas'}), 400

        data = request.get_json(force=True)
        print(f"Received data: {data}")
        if not data:
            return jsonify({'status': 'error', 'message': 'Ingen data mottagen'}), 400

        uid = data.get('uid')
        if not uid or not isinstance(uid, str) or len(uid.strip()) == 0:
            return jsonify({'status': 'error', 'message': 'UID saknas eller ogiltig'}), 400

        source = data.get('source')
        if not source or not isinstance(source, str) or len(source.strip()) == 0:
            return jsonify({'status': 'error', 'message': 'Source saknas eller ogiltig'}), 400

        user = RegisteredUsers.query.filter_by(tag_id=uid).first()
        if not user:
            new_entry = NFCLoginLog(
                uid=uid,
                message='Ogiltigt Tagg-ID',
                success=False,
                source=source,
                user_name=None,
                is_processed=False,
                whoami=whoami
            )
            db.session.add(new_entry)
            db.session.commit()
            return jsonify({'status': 'error', 'message': 'Tag ogiltig'}), 404

        now = to_stockholm_time(datetime.now())

        print(user.last_scan_time, now, (now - user.last_scan_time) <= timedelta(minutes=1))

        if user.last_scan_time and (now - user.last_scan_time) <= timedelta(minutes=1):
            new_entry = NFCLoginLog(
                uid=uid,
                message='Vänligen vänta en minut innan du skannar igen',
                success=False,
                source=source,
                user_name=user.user_name,
                is_processed=False,
                whoami=whoami
            )
            db.session.add(new_entry)
            db.session.commit()
            return jsonify({'status': 'wait', 'message': 'Vänligen vänta en minut innan du skannar igen'}), 429

        user.is_logged_in = not user.is_logged_in
        user.last_scan_time = to_stockholm_time(datetime.now())
        db.session.commit()

        message = f"Välkommen {user.user_name}!" if user.is_logged_in else f"Hejdå {user.user_name}!"
        print(message)
        new_entry = NFCLoginLog(
            uid=uid,
            message=message,
            success=True,
            source=source,
            user_name=user.user_name,
            is_processed=False,
            whoami=whoami
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({
            'success': True,
            'name': user.user_name,
            'new_state': 'inloggad' if user.is_logged_in else 'utloggad',
            'message': message
        }), 200

    except SQLAlchemyError as db_err:
        current_app.logger.error(f"Database error: {db_err}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Databasfel'}), 500

    except Exception as ex:
        current_app.logger.error(f"Unhandled exception: {ex}")
        return jsonify({'status': 'error', 'message': 'Internt serverfel'}), 500


@nfc_backend_blueprint.route('/scan-store-register', methods=['POST'])
@require_nfc_token
def scan_store_register():
    try:
        data = request.get_json()
        uid = data.get('uid')
        source = data.get('source')
        scan_type = data.get('scan_type')
        whoami = request.headers.get('whoami')
        if not source:
            return jsonify({'status': 'error', 'message': 'Source saknas'}), 400
        if not uid:
            return jsonify({'status': 'error', 'message': 'UID saknas'}), 400
        if not scan_type:
            return jsonify({'status': 'error', 'message': 'Scan_type saknas'}), 400
        if not isinstance(uid, str) or len(uid.strip()) == 0:
            return jsonify({'status': 'error', 'message': 'Ogiltig UID'}), 400
        if not whoami:
            return jsonify({'status': 'error', 'message': 'Identifier header saknas'}), 400

        buffer_entry = NFCScanBuffer(uid=uid, is_processed=False, source=source, scan_type=scan_type, whoami=whoami)

        db.session.add(buffer_entry)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'UID lagrad'}), 200
    except Exception as e:
        current_app.logger.error(f"Fel i scan_store_register: {e}")
        return jsonify({'status': 'error', 'message': 'Serverfel'}), 500


# TODO: Replacing the existing polling system with a more efficient approach
#  SSE (Server-Sent Events) or WebSockets would be more efficient for real-time updates.
@nfc_backend_blueprint.route('/login-sse')
# @require_nfc_token
def login_sse():
    whoami = request.args.get('whoami')

    @stream_with_context
    def event_stream():
        last_seen_id = None

        while True:
            entry = NFCLoginLog.query.filter_by(is_processed=False).filter_by(source=whoami).order_by(NFCLoginLog.created_at.desc()).first()

            if entry and entry.id != last_seen_id:
                payload = {
                    'id': entry.id,
                    'uid': entry.uid,
                    'user_name': entry.user_name,
                    'message': entry.message,
                    'success': entry.success,
                    'created_at': entry.created_at.isoformat()
                }

                # Mark processed
                entry.is_processed = True
                db.session.commit()

                last_seen_id = entry.id
                yield f"data: {json.dumps(payload)}\n\n"

    response = Response(event_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response


