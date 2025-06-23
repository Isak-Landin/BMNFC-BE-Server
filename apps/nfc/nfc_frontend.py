from flask import Blueprint, render_template, request, jsonify


nfc_frontend_blueprint = Blueprint('nfc_frontend_blueprint', __name__, url_prefix='/nfc/frontend')


# TODO: Make sure that this is client/server split compatible

# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.


@nfc_frontend_blueprint.route('/', methods=['GET'])
def nfc_frontend():
    """
    This endpoint serves the NFC frontend page.
    It renders the nfc_frontend.html template.
    """
    return render_template('nfc_frontend.html')