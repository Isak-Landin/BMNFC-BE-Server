from datetime import datetime, timedelta

import pytz
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from apps.login.models import UserLogin
from apps.manage.models import RegisteredUsers
from apps.manage.models import AdminUser

from flask_login import login_required, login_user, current_user, logout_user
from apps.extensions import db

# Decorator
from apps.decorators import admin_required

# Convert time to Stockholm timezone
from apps.extensions import to_stockholm_time

manage_blueprint = Blueprint('manage_blueprint', __name__, url_prefix='/manage')
# This page should allow the admin to manage existing users
# This includes:
# 1. Adding new users
# 2. Removing users
# 3. Updating user information


# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.


# TODO: Make sure that this is client/server split compatible

@manage_blueprint.route('/login', methods=['GET', 'POST'])
def manage_login():
    # TODO Use this page to log in as admin
    #  The admin will be able to log in using a username and password
    #  The admin will be redirected to the overview page after logging in
    # For now, let's just redirect to the same login page welcoming the user

    # Start implementing the login functionality
    # Check if the user is already logged in
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password are correct
        admin_user = AdminUser.query.filter_by(username=username).first()
        if admin_user and admin_user.check_password(password):
            login_user(admin_user)
            return redirect(url_for('manage_blueprint.manage_overview'))
        else:
            # If the login fails, you can render an error message or redirect
            return render_template('manage_login.html', error_message="Invalid username or password")

    # If the request method is GET, render the login page
    return render_template('manage_login.html')


@manage_blueprint.route('/logout', methods=['POST'])
# @admin_required
def manage_logout():
    logout_user()
    return redirect(url_for('manage_blueprint.manage_login'))


@manage_blueprint.route('/overview', methods=['GET'])
# @admin_required
def manage_overview():
    # Retrieve all registered users
    result_registered = RegisteredUsers.query.all()

    # Retrieve registered users who are currently marked as logged in
    result_logged_in = RegisteredUsers.query.filter_by(is_logged_in=True).all()

    # Convert timestamps to Stockholm time for both lists
    for user in result_registered:
        if user.last_scan_time:
            user.last_scan_time = to_stockholm_time(user.last_scan_time)
        if user.registration_time:
            user.registration_time = to_stockholm_time(user.registration_time)

    for user in result_logged_in:
        if user.last_scan_time:
            user.last_scan_time = to_stockholm_time(user.last_scan_time)
        if user.registration_time:
            user.registration_time = to_stockholm_time(user.registration_time)

    # Retrieve all admins (for now we just show usernames)
    result_admins = AdminUser.query.all()

    return render_template(
        'manage_overview.html',
        registered_users=result_registered,
        logged_in_users=result_logged_in,
        admins=result_admins
    )


@manage_blueprint.route('/add_user', methods=['POST'])
# @admin_required
def manage_add_user():
    name = request.form.get('name')
    tag_id = request.form.get('tag_id', None)  # Allow tag_id to be optional
    location = request.form.get('location')
    is_active = request.form.get('is_active') in ['true', 'on', 'True']
    is_logged_in = request.form.get('is_logged_in') in ['true', 'on', 'True']

    if not name:
        return jsonify({'success': False, 'message': 'Namn krävs.'}), 400

    # Check for existing tag_id
    if tag_id:
        existing_tag = RegisteredUsers.query.filter_by(tag_id=tag_id).first()
        if existing_tag:
            return jsonify({'success': False, 'message': f'Tagg-ID "{tag_id}" är redan registrerat.'}), 409
    else:
        tag_id = None  # Allow tag_id to be optional

    # Check for existing user_name
    existing_name = RegisteredUsers.query.filter_by(user_name=name).first()
    if existing_name:
        return jsonify({'success': False, 'message': f'Namn "{name}" är redan registrerat.'}), 409

    # Timezone-aware registration_time
    stockholm_time = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('Europe/Stockholm'))

    new_user = RegisteredUsers(
        user_name=name,
        tag_id=tag_id,
        location=location,
        registration_time=stockholm_time,
        is_active=is_active,
        is_logged_in=is_logged_in
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Databasfel: {str(e)}'}), 500

    return jsonify({'success': True, 'message': f'Användaren "{name}" tillagd.'}), 200


@manage_blueprint.route('/delete_user/<int:user_id>', methods=['POST'])
# @admin_required
def manage_delete_user(user_id):
    user_to_remove = RegisteredUsers.query.get_or_404(user_id)

    db.session.delete(user_to_remove)
    db.session.commit()

    return jsonify({'success': True}), 200


@manage_blueprint.route('/add_admin', methods=['POST'])
# @admin_required
def manage_add_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Både användarnamn och lösenord krävs.'}), 400

    if AdminUser.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Användarnamnet är redan upptaget.'}), 409

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Lösenordet måste vara minst 6 tecken långt.'}), 400

    new_admin = AdminUser(username, password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'success': True}), 201


@manage_blueprint.route('/edit_admin/<int:admin_id>', methods=['POST'])
def manage_edit_admin(admin_id):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Ingen data mottagen.'}), 400

    # Fetch admin from DB
    admin = AdminUser.query.get_or_404(admin_id)

    new_username = data.get('username', admin.username)
    new_password = data.get('password', None)  # Optional: only update if provided
    print(new_password)

    # Validate required fields
    if not new_username:
        return jsonify({'success': False, 'message': 'Användarnamn krävs.'}), 400

    # Check for duplicate username (excluding current admin)
    if AdminUser.query.filter(AdminUser.id != admin_id, AdminUser.username == new_username).first():
        return jsonify({'success': False, 'message': 'Användarnamnet är redan upptaget.'}), 409

    # Apply updates
    if admin.username != new_username:
        admin.username = new_username
    if new_password:
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Lösenordet måste vara minst 6 tecken långt.'}), 400
        admin.set_password(new_password)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Databasfel: {str(e)}'}), 500

    return jsonify({'success': True, 'message': 'Adminuppdatering lyckades.', 'admin_id': admin.id}), 200


@manage_blueprint.route('/delete_admin/<int:admin_id>', methods=['POST'])
# @admin_required
def manage_delete_admin(admin_id):
    admin_to_delete = AdminUser.query.get_or_404(admin_id)

    if admin_to_delete.id == current_user.id:
        return jsonify({'success': False, 'message': 'Du kan inte ta bort dig själv.'}), 400

    db.session.delete(admin_to_delete)
    db.session.commit()
    db.session.commit()

    return jsonify({'success': True}), 200


@manage_blueprint.route('/edit/<int:user_id>', methods=['POST'])
def manage_edit_user(user_id):
    from sqlalchemy.exc import IntegrityError

    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return False

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Ingen data mottagen.'}), 400

    user = RegisteredUsers.query.get_or_404(user_id)

    new_name = data.get('name')
    new_tag_id = data.get('tag_id')  # Can be None
    new_location = data.get('location', user.location)
    new_is_active = str_to_bool(data.get('is_active', user.is_active))
    new_is_logged_in = str_to_bool(data.get('is_logged_in', user.is_logged_in))

    if not new_name:
        return jsonify({'success': False, 'message': 'Namn krävs.'}), 400

    # Duplicate name check
    if RegisteredUsers.query.filter(RegisteredUsers.id != user_id, RegisteredUsers.user_name == new_name).first():
        return jsonify({'success': False, 'message': 'Namn är redan upptaget.'}), 409

    # Duplicate tag check (only if tag_id is provided)
    if new_tag_id:
        conflict_user = RegisteredUsers.query.filter(RegisteredUsers.id != user_id, RegisteredUsers.tag_id == new_tag_id).first()
        if conflict_user:
            return jsonify({'success': False, 'message': f'Tagg-ID "{new_tag_id}" är redan registrerat.'}), 409

    # Apply changes
    user.user_name = new_name
    if new_tag_id is not None:
        user.tag_id = new_tag_id
    user.location = new_location
    user.is_active = new_is_active

    # Handle login toggle
    if not user.is_logged_in and new_is_logged_in:
        user.last_scan_time = to_stockholm_time(datetime.now())
    user.is_logged_in = new_is_logged_in

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Uppdateringen lyckades.', 'user_id': user.id}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Databasfel: Tagg-ID måste vara unikt.'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Fel: {str(e)}'}), 500



@manage_blueprint.route('/logout_user/<int:user_id>', methods=['POST'])
# @admin_required
def manage_logout_user(user_id):
    user = RegisteredUsers.query.get_or_404(user_id)
    user.is_logged_in = False
    db.session.commit()

    return jsonify({
        'success': True,
        'user_id': user.id,
        'is_logged_in': user.is_logged_in
    }), 200


"""
# TODO: Implement the NFC tag writing functionality
#  think about the need to use any writing at all, or if we can just use the UID as a string
#  If we are to write to the NFC tag, we need to ensure that the tag can be written to from a phone or the nfc writer
@manage_blueprint.route('/write_tag/<int:user_id>', methods=['POST'])
# @admin_required
def write_nfc_tag(user_id):
    user = RegisteredUsers.query.get_or_404(user_id)
    new_value = request.json.get('tag_value')

    if not new_value or len(new_value) > 16:
        return jsonify({'success': False, 'message': 'Tag value must be 1–16 characters.'}), 400

    try:
        success = True
        if not success:
            return jsonify({'success': False, 'message': 'Failed to write to NFC tag.'}), 500

        user.tag_id = new_value
        db.session.commit()
        return jsonify({'success': True, 'tag_id': new_value}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
"""

@manage_blueprint.route('/add_card/<int:user_id>', methods=['POST'])
# @admin_required
def add_card_to_user(user_id):
    user_id = user_id
    uid = request.json.get('uid')

    if not user_id or not uid:
        return jsonify({'success': False, 'message': 'User ID and UID are required.'}), 400

    # Check if UID is already assigned to another user
    existing_user = RegisteredUsers.query.filter_by(tag_id=uid).first()
    if existing_user and existing_user.id != user_id:
        return jsonify({'success': False, 'message': f'UID {uid} is already assigned to another user.'}), 409

    user = RegisteredUsers.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    user.tag_id = uid
    db.session.commit()

    return jsonify(
        {'success': True, 'message': f'UID {uid} has been assigned to user {user.user_name}.', 'user_id': user.id,
         'uid': uid})


@manage_blueprint.route('/remove_card/<int:user_id>', methods=['POST'])
# @admin_required
def remove_card_from_user(user_id):

    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required.'}), 400

    user = RegisteredUsers.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    user.tag_id = None
    db.session.commit()

    return jsonify({'success': True, 'message': f'UID removed from user {user.user_name}.', 'user_id': user.id})


# Expected login logic for NFC card login to match the commented-out code in the original snippet
"""
@manage_blueprint.route('/login', methods=['POST'])
def login_via_card():
    uid = request.json.get('uid')  # From NFC scanner (Raspberry)

    if not uid:
        return jsonify({'success': False, 'message': 'UID is required.'}), 400

    user = RegisteredUsers.query.filter_by(tag_id=uid).first()

    if not user:
        return jsonify({'success': False, 'message': 'Card not recognized.'}), 404

    if not user.is_active:
        return jsonify({'success': False, 'message': 'User is not active.'}), 403

    # Mark user as logged in
    user.is_logged_in = True
    db.session.commit()

    return jsonify({'success': True, 'message': f'Welcome, {user.user_name}!', 'user_id': user.id})

"""

