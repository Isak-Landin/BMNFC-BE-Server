from flask import Blueprint, render_template, request, redirect, url_for

from flask import Response
from apps.manage.models import RegisteredUsers
from pytz import timezone
from apps.extensions import to_stockholm_time

export_blueprint = Blueprint('export_blueprint', __name__, url_prefix='/export')


# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.


# This page should export the list of logged-in users to a CSV file and/or directly on the page
# TODO: Make sure that this is client/server split compatible

@export_blueprint.route('/', methods=['GET'])
def export():
    # Retrieve all logged-in users from database to result
    result = RegisteredUsers.query.filter_by(is_logged_in=True).all()

    # Check if logged-in users exist
    if len(result) > 0:
        # Convert scan times to Stockholm time
        for user in result:
            if user.last_scan_time:
                user.last_scan_time = to_stockholm_time(user.last_scan_time)
        users = result
    else:
        users = None

    return render_template('export.html', users=users)


@export_blueprint.route('/download', methods=['POST', 'GET'])
def download_csv():
    users = RegisteredUsers.query.filter_by(is_logged_in=True).all()

    csv_data = "Namn,Tag ID,Inloggad Tid\n"
    for user in users:
        if user.last_scan_time:
            formatted_time = to_stockholm_time(user.last_scan_time).strftime('%Y-%m-%d %H:%M')
        else:
            formatted_time = "—"

        csv_data += f"{user.user_name},{user.tag_id},{formatted_time}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=dagens_inloggade.csv"}
    )
