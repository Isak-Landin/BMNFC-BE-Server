from sqlalchemy import Column, Integer, String, Boolean, DateTime
from apps.extensions import db

from datetime import datetime
from apps.extensions import to_stockholm_time


# This file is part of a proprietary system jointly owned by Isak Landin and Compliq IT AB.
# Contact either party for licensing or usage inquiries.


class NFCScanBuffer(db.Model):
    __tablename__ = 'NFCScanBuffer'

    id = Column(Integer, primary_key=True)
    uid = Column(String(120), nullable=False)
    scan_type = Column(String(120), nullable=False)  # e.g., 'register', 'login
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=to_stockholm_time(datetime.now()), nullable=False)
    source = Column(String(120), nullable=False)  # e.g., 'nfc_reader_frontend', 'nfc_reader_container'
    whoami = Column(String(120), nullable=False)  # Which frontend that has sent the request

    def __init__(self, uid, source, whoami, scan_type='register', is_processed=False, timestamp=None):
        if not uid or not source:
            raise ValueError("Tag ID and source are required for TagsToRegister")
        self.uid = uid
        self.scan_type = scan_type
        self.source = source
        self.is_processed = is_processed
        self.created_at = timestamp or to_stockholm_time(datetime.now())
        self.whoami = whoami

    def __repr__(self):
        return f"<TagsToRegister {self.tag_id} - Type: {self.type}, Processed: {self.is_processed}, Source: {self.source}>"


class NFCLoginLog(db.Model):
    __tablename__ = 'NFCLoginLog'

    id = Column(Integer, primary_key=True)
    uid = Column(String(120), nullable=False)
    user_name = Column(String(120), nullable=True)  # Might be None if unknown UID
    message = Column(String(255), nullable=False)
    success = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=to_stockholm_time(datetime.now()), nullable=False)
    source = Column(String(120), nullable=False, default='backend')  # e.g., 'nfc_reader_frontend', 'nfc_reader_container'
    whoami = Column(String(120), nullable=False)  # Which frontend that has sent the request

    is_processed = Column(Boolean, default=False, nullable=False)

    def __init__(self, uid, message, success, whoami, source='backend', user_name=None, is_processed=False):
        self.uid = uid
        self.message = message
        self.success = success
        self.source = source
        self.user_name = user_name
        self.created_at = to_stockholm_time(datetime.now())
        self.is_processed = is_processed
        self.whoami = whoami

    def __repr__(self):
        return f"<NFCLoginLog uid={self.uid} success={self.success} user={self.user_name}>"