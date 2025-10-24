import re
import random
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .sms_utils import send_verification_code, check_verification_code

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements."""
    if (len(password) < 8 or
        not re.search(r"[A-Z]", password) or
        not re.search(r"[a-z]", password) or
        not re.search(r"[0-9]", password) or
        not re.search(r"[@$!%*?&]", password)):
        return False
    return True

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        number = request.form.get('number')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(number) < 10:
            flash('Phone number must be valid (at least 10 digits).', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not is_strong_password(password1):
            flash('Password must be at least 8 characters and include an uppercase, '
                  'lowercase, number, and special character.', category='error')
        else:
            hashed_pw = generate_password_hash(password1, method='pbkdf2:sha256')

            new_user = User(email=email, first_name=first_name, last_name=last_name, number=number, password=password1, verified=False)
            db.session.add(new_user)
            db.session.commit()
            send_verification_code(new_user.number)

            flash('Account created! Please check your phone for a verification code.', category='success')
            return redirect(url_for('views.verify_phone', user_id=new_user.id))

    return render_template("sign_up.html", user=current_user)

@auth.route("/verify_phone/<int:user_id>", methods=["GET", "POST"])
def verify_phone(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        code = request.form.get("code")
        status = check_verification_code(user.phone, code)
        if status == "approved":
            user.phone_verified = True
            db.session.commit()
            login_user(user, remember=True)
            flash("Phone verified, you're logged in!", "success")
            return redirect(url_for("views.home"))
        else:
            flash("Invalid code. Please try again.", "error")
    return render_template("verify_phone.html", phone=user.phone)



