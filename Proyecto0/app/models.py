from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from time import time
import jwt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    eventos = db.relationship('Evento', backref='author', lazy='dynamic')

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
            
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Evento(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column( db.String(255) )
    lugar = db.Column( db.String(255) )
    direccion = db.Column( db.String(255) )
    fechaInicio = db.Column( db.DateTime() )
    fechaFin = db.Column( db.DateTime() )
    categoria = db.Column( db.String(255) )
    evento = db.Column( db.String(255) )
    fechaCreacion = db.Column( db.DateTime() )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.nombre)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


    