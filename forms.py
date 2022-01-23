from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, InputRequired, EqualTo


class ContactForm(FlaskForm):
    fullname = StringField('Fullname', validators=[DataRequired(), Length(min=-1, max=80, message='You cannot have more than 80 characters')])
    email = StringField('E-Mail', validators=[Email(), Length(min=-1, max=200, message='You cannot have more than 200 characters')])
    G_name = StringField('Guardiun Name', validators=[DataRequired(), Length(min=-1, max=80, message='You cannot have more than 80 characters')])
    G_W = StringField('Guardiun Whatsapp', validators=[Length(min=-1, max=20, message='You cannot have more than 20 characters')])
    C_W = StringField('Child Whatsapp', validators=[Length(min=-1, max=20, message='You cannot have more than 20 characters')])
    phone = StringField('Phone', validators=[Length(min=-1, max=20, message='You cannot have more than 20 characters')])
   
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email('Invalid Email')])
    username = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    remember = BooleanField('remember me')
