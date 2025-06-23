from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import pytz
from apps.extensions import to_stockholm_time
from apps.manage.models import RegisteredUsers
from apps.nfc.models import NFCScanBuffer
from apps.nfc.models import NFCLoginLog
from apps.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import os
from flask_wtf import csrf

from sqlalchemy import and_

NFC_SECRET_TOKEN = os.getenv('NFC_SECRET_TOKEN', 'default_token')


nfc_blueprint = Blueprint('nfc_blueprint', __name__, url_prefix='/nfc')


# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.


# TODO: Make sure that this is client/server split compatible


@nfc_blueprint.route('/wait-for-registration-uid', methods=['GET'])
def wait_for_registration_uid():
    """
    This endpoint waits for a UID to be scanned.
    It returns a JSON response with the status and message.
    """

    new_awaiting_row = NFCScanBuffer.query.filter_by(is_processed=False, scan_type='register').first()
    if new_awaiting_row:
        new_awaiting_row.is_processed = True

        # This is to ensure that no false positives are returned
        #  if there are any unprocessed rows, they will be marked as processed
        all_unprocessed_rows = NFCScanBuffer.query.filter_by(is_processed=False).all()
        for row in all_unprocessed_rows:
            row.is_processed = True
        db.session.commit()
        return jsonify({'success': True, 'uid': new_awaiting_row.uid}), 200

    return jsonify({'success': 'waiting', 'message': 'Väntar på NFC-tag att skanna...'}), 202


@nfc_blueprint.route('/wait-for-login-uid', methods=['POST'])
def wait_for_login_uid():
    rows = NFCLoginLog.query.filter_by(is_processed=False, source='nfc_reader_container')\
                            .order_by(NFCLoginLog.created_at.asc())\
                            .limit(3).all()

    if rows:
        data = [{
            'id': row.id,  # 👈 Add ID so we can ack later
            'uid': row.uid,
            'message': row.message,
            'success': row.success,
            'user_name': row.user_name,
            'created_at': row.created_at.isoformat(),
            'source': row.source
        } for row in rows]

        return jsonify({'success': True, 'data': data}), 200

    return jsonify({'success': 'waiting', 'message': 'Väntar på NFC-tag att skanna...'}), 202


@nfc_blueprint.route('/confirm-processed', methods=['POST'])
def confirm_processed():
    try:
        data = request.get_json(force=True)
        ids = data.get('ids', [])

        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return jsonify({'success': False, 'message': 'Ogiltiga ID:n'}), 400

        NFCLoginLog.query.filter(NFCLoginLog.id.in_(ids)).update(
            {NFCLoginLog.is_processed: True}, synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to mark processed: {e}")
        return jsonify({'success': False, 'message': 'Serverfel'}), 500



