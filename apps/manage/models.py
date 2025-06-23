from apps.extensions import db
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from apps.extensions import to_stockholm_time


# Swedish timezone

# This file is part of a proprietary system jointly owned by Isak Landin and Compliq IT AB.
# Contact either party for licensing or usage inquiries.


class RegisteredUsers(db.Model):
    __tablename__ = 'registered_users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), nullable=False, unique=True)
    tag_id = db.Column(db.String(120), nullable=True, unique=True)
    registration_time = db.Column(db.DateTime(timezone=True), default=to_stockholm_time(datetime.now()), nullable=False)
    last_scan_time = db.Column(db.DateTime(timezone=True), default=to_stockholm_time(datetime.now()), nullable=True)
    location = db.Column(db.String(120), nullable=True)  # Maybe for the office and for "boden" - TODO Should be removed
    is_logged_in = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)  # To check if the user is active or not

    def __init__(self, user_name, tag_id, location=None, registration_time=None, is_logged_in=True, is_active=True):
        if not user_name or not tag_id:
            raise ValueError("Username and tag ID are required for RegisteredUsers")
        self.user_name = user_name
        self.tag_id = tag_id
        self.location = location
        self.registration_time = registration_time or to_stockholm_time(datetime.now())
        self.is_logged_in = is_logged_in
        self.is_active = is_active

    def __repr__(self):
        return f"<AllRegisteredUsers {self.user_name} - Registered: {self.registration_time}>"


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, password):
        if not username or not password:
            raise ValueError("Username and password are required for AdminUser")
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<AdminUser {self.username}>"
