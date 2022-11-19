from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from plasma.models import User


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    contact_no = StringField('Contact Number',
                           validators=[DataRequired(), Length(min=2, max=20)])
    gender = RadioField('Gender', choices=['Male', 'Female'])
    role = RadioField('Role', choices=['Donar', 'Patients'])
    blood_group = StringField('Blood Group', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class SearchForm(FlaskForm):
    blood_group = StringField('Blood Group',
                        validators=[DataRequired()])
    submit = SubmitField('Search')

class MessageForm(FlaskForm):
    to_id = StringField('Donor Email', validators=[DataRequired()])
    message = StringField('Enter Message', validators=[DataRequired()])
    submit = SubmitField('Send')
