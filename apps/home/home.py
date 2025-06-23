from flask import Blueprint, render_template, request, redirect, url_for


home_blueprint = Blueprint('home_blueprint', __name__, url_prefix='/')


# NFC-tag-system
# Copyright (c) 2025 Isak Landin
# Copyright (c) 2025 Compliq IT AB
#
# Proprietary software. All rights reserved.
# Unauthorized use, copying, or distribution is prohibited.

# TODO: Make sure that this is client/server split compatible

# We have the home page to allow the user to select where they want to go
# They have two options as of now:
# 1. Login page
# 2. Export page
@home_blueprint.route('/')
def home():
    return render_template('home.html')