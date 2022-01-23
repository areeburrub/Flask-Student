from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from datetime import datetime
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Contact(db.Model):


    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200), nullable=True, unique=True)
    G_name = db.Column(db.String(80), nullable=False)
    G_W = db.Column(db.String(20), nullable=True, unique=False)
    C_W = db.Column(db.String(20), nullable=True, unique=False)
    phone = db.Column(db.String(20), nullable=True, unique=False)
    batch = db.Column(db.String(20), nullable=False)
    uid = db.Column(db.String(80), nullable=False, default=secrets.token_urlsafe(8))
    

    def __repr__(self):
        return '<Contacts %r>' % self.fullname

class Att_T(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), nullable=False)
    present = db.Column(db.String(80), nullable=False)
    absent = db.Column(db.String(80), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adid = db.Column(db.String(15), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean, unique=False, default=False)
    userad = db.Column(db.Boolean, unique=False, default=False)
    

class Remarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rid = db.Column(db.String(15), nullable = False)
    by = db.Column(db.String(80), nullable = False)
    byname = db.Column(db.String(15), nullable = False)
    to = db.Column(db.String(80), nullable = False)
    text = db.Column(db.String(15), nullable = False)
    date = db.Column(db.DateTime, default = datetime.utcnow)
    privacy = db.Column(db.String(15), nullable = False, default="public")

class Att(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attid = db.Column(db.String(15), nullable = False)
    byname = db.Column(db.String(80), nullable = False)
    of = db.Column(db.String(80), nullable = False)
    purpose = db.Column(db.String(15), nullable = False)
    status = db.Column(db.Boolean, unique=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendid = db.Column(db.String(15), nullable = False)
    byname = db.Column(db.String(80), nullable = False)
    Class = db.Column(db.String(40), nullable = False)
    batch = db.Column(db.String(40), nullable = False)
    present = db.Column(db.String(45), nullable = False)
    absent = db.Column(db.String(45), nullable = False)
    date = db.Column(db.DateTime, default = datetime.utcnow)

class Allow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable = False)
    allowed = db.Column(db.String(80), nullable = False)
    