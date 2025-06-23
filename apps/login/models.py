from datetime import datetime
from apps.extensions import db

# This file is part of a proprietary system jointly owned by Isak Landin and Compliq IT AB.
# Contact either party for licensing or usage inquiries.


# Define the UserLogin model
class UserLogin(db.Model):
    __tablename__ = 'user_logins'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), nullable=False)
    tag_id = db.Column(db.String(120), nullable=False, unique=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(120), nullable=True)  # Maybe for the office and for "boden"
    is_logged_in = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<UserLogin {self.user_name} - Logged in: {self.is_logged_in}>"
