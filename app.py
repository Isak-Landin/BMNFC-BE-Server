from flask import Flask, jsonify
import os
from datetime import datetime

from dotenv import load_dotenv
from apps.export.export import export_blueprint
from apps.home.home import home_blueprint
from apps.login.login import login_blueprint
from apps.manage.manage import manage_blueprint
from apps.nfc.nfc import nfc_blueprint
from apps.nfc.nfc_backend import nfc_backend_blueprint
from apps.nfc.nfc_frontend import nfc_frontend_blueprint

from apps.manage.models import AdminUser
from apps.login.models import UserLogin
from apps.manage.models import RegisteredUsers

from apps.extensions import login_manager
from apps.extensions import db

# For regex search
import re

# Protect against CSRF attacks
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

# Import BackgroundScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# Import logging for info level logging
import logging

# Import the custom function to convert to Stockholm time
from apps.extensions import to_stockholm_time


# Load environment variables from .env file
load_dotenv()


# Login manager needs user loader to manage logins on admin page
@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


# Logger to log at info level
# Basic logging config for production
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
logger = logging.getLogger(__name__)
logging.FileHandler("app.log")


# Register the application and configure the database
def create_app():

    _app = Flask(__name__, template_folder='static/templates', static_folder='static')
    _app.register_blueprint(home_blueprint)
    _app.register_blueprint(login_blueprint)
    _app.register_blueprint(export_blueprint)
    _app.register_blueprint(nfc_blueprint)
    _app.register_blueprint(nfc_backend_blueprint)
    _app.register_blueprint(nfc_frontend_blueprint)

    # Register the manage blueprint for admin functionalities
    _app.register_blueprint(manage_blueprint)

    # Read environment variables (fixed names)
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', 5433)

    # Configure database URI
    _app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'defaultsecret')

    # Initialize the database with the app
    db.init_app(_app)

    # Initialize the login manager
    login_manager.init_app(_app)
    login_manager.login_view = 'manage_blueprint.manage_login'

    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(_app)
    csrf.exempt(nfc_backend_blueprint)  # Exempt NFC backend endpoint from CSRF protection
    csrf.exempt(nfc_blueprint)  # Exempt NFC endpoint from CSRF protection

    # Ensure the database for registered users resets is_logged_in values at 00:00 every day
    scheduler = BackgroundScheduler(timezone='Europe/Stockholm')

    def reset_logged_in():
        with app.app_context():
            db.session.query(RegisteredUsers).update({RegisteredUsers.is_logged_in: False})
            db.session.commit()
            # Log the reset action
            logger.info(f"Reset logged_in status for all users at {to_stockholm_time(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}")

    scheduler.add_job(reset_logged_in, 'cron', hour=0, minute=0)
    scheduler.start()

    return _app


# Create the app instance
app = create_app()
# Create all the tables in the database


# Adding regex filter to the app
@app.template_filter('regex_search')
def regex_search(s, pattern, ignorecase=False):
    flags = re.IGNORECASE if ignorecase else 0
    match = re.search(pattern, s, flags)
    return match.group() if match else ''


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'success': False, 'message': 'CSRF-token saknas eller ogiltig.'}), 400


with app.app_context():
    db.create_all()
