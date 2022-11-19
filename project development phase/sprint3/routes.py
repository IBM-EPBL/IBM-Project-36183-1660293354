from flask import render_template, url_for, flash, redirect, request
from plasma import app, db, bcrypt
from plasma.forms import RegistrationForm, SearchForm, LoginForm, MessageForm
from plasma.models import User, Message
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os, time
from functools import wraps
from sqlalchemy import and_, or_, not_
import ibm_db

@app.route("/user_operation", methods=['GET', 'POST'])
@login_required()
def user_operation():
    form1 = SearchForm()
    form2 = MessageForm()
    donors = []

    if form1.validate_on_submit() and form1.submit.data:
        donors = []
        blood_group = form1.blood_group.data
        data = User.query.filter_by(blood_group=blood_group, role='Donar').all()
        print('data', data)
        if data:
            for datam in data:
                if datam.email != current_user.email:
                    donors.append([datam.name, datam.email, datam.contact_no])

    if form2.validate_on_submit() and form2.submit.data:
        to_id = form2.to_id.data
        message = form2.message.data
        print(to_id, message)
        add_message = Message(from_id=current_user.email, to_id=to_id, message=message)
        db.session.add(add_message)
        db.session.commit()
        #ibm_sync('message', [add_message.id, current_user.email, form2.to_id.data, form2.message.data])

    messages = []
    text = Message.query.filter_by(to_id=current_user.email).all()
    if text:
        for t in text:
            messages.append([t.from_id, t.message])

    if len(donors)>0:
        donor_flag = True
    else:
        donor_flag = False
    return render_template('user_operation.html', title="Dashboard", form1=form1, form2=form2, 
        donors=donors, messages=messages, donor_flag=donor_flag)

