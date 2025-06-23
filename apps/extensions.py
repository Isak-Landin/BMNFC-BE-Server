from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pytz
from datetime import datetime

# This file is part of a proprietary system jointly owned by Isak Landin and Compliq IT AB.
# Contact either party for licensing or usage inquiries.


login_manager = LoginManager()
db = SQLAlchemy()


def to_stockholm_time(dt):
    if dt is None:
        return None
    stockholm = pytz.timezone('Europe/Stockholm')
    # If dt is naive (no timezone), treat it as UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(stockholm)