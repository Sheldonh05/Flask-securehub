from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user, login_user, login_required, logout_user
from .models import Note, User
from . import db
from .sms_utils import send_verification_code, check_verification_code
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/verify_phone/<int:user_id>', methods=['GET', 'POST'])
def verify_phone(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'GET':
        if not user.verified:
            status = send_verification_code(user.number)
            if status == "pending":
                flash('Verification code sent to your phone!', 'info')
            else:
                flash('Failed to send verification code. Try again later.', 'error')

    if request.method == 'POST':
        code_entered = request.form.get('code')

        status = check_verification_code(user.number, code_entered)
        if status == "approved":
            user.verified = True
            db.session.commit()

            login_user(user, remember=True)
            flash('Phone number verified! You are logged in.', 'success')
            return redirect(url_for('views.home'))
        else:
            flash('Invalid code. Please try again.', 'error')

    return render_template("verify_phone.html", user=user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})