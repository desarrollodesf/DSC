import os.path
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap
from datetime import datetime
import pytz
from tzlocal import get_localzone

def setup_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
api = Api(app)
ma = Marshmallow(app)
bootstrap = Bootstrap(app)

login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
from app.models import Evento, User

if not os.path.isfile(app.config['SQLALCHEMY_DATABASE_URI']):
    setup_database(app)

class Evento_Schema(ma.Schema):

    class Meta:

        fields = ("id", "nombre", "lugar", "direccion", "fechaInicio", "fechaFin", "categoria", "evento", "fechaCreacion", "user_id")

   
post_schema = Evento_Schema()

posts_schema = Evento_Schema(many = True)

class Eventos(Resource):

    def get(self):

        eventos = Evento.query.all()

        return posts_schema.dump(eventos)

    def post(self):

            nuevo_evento = Evento(
                nombre = request.json['nombre'],
                lugar = request.json['lugar'],
                direccion = request.json['direccion'],
                fechaInicio = datetime.strptime(datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/New_York")).strftime('%Y-%m-%dT%H:%M'),'%Y-%m-%dT%H:%M'),
                fechaFin = datetime.strptime(datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/New_York")).strftime('%Y-%m-%dT%H:%M'),'%Y-%m-%dT%H:%M'),
                categoria = request.json['categoria'],
                evento = request.json['evento'],
                fechaCreacion = datetime.strptime(datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/New_York")).strftime('%Y-%m-%dT%H:%M'),'%Y-%m-%dT%H:%M'),
                user_id = request.json['user_id']     
            )

            db.session.add(nuevo_evento)

            db.session.commit()

            return post_schema.dump(nuevo_evento)

class EventosPorUsuario(Resource):

    def get(self, id_usuario):

        events = Evento.query.filter_by(user_id=id_usuario)

        return posts_schema.dump(events)

class PorEvento(Resource):

    def get(self, id_evento):

        if Evento.query.filter_by(id_evento).first() is None:
            return 'Evento no existe existe', 400

        evento = Evento.query.get_or_404(id_evento)
        return post_schema.dump(evento)

    def put(self, id_evento):

        evento = Evento.query.get_or_404(id_evento)


        if 'nombre' in request.json:

            evento.nombre = request.json['nombre']

        if 'lugar' in request.json:

            evento.lugar = request.json['lugar']

        if 'dirección' in request.json:

            evento.dirección = request.json['direccion']

        if 'fechaInicio' in request.json:

            evento.fechaInicio = request.json['fechaInicio']

        if 'fechaFin' in request.json:

            evento.fechaFin = request.json['fechaFin']

        if 'categoria' in request.json:

            evento.categoria = request.json['categoria']

        if 'evento' in request.json:

            evento.categoria = request.json['evento']
        
        if 'user_id' in request.json:

            evento.categoria = request.json['user_id']
        
        db.session.commit()

        return post_schema.dump(evento)


    def delete(self, id_evento):

        if Evento.query.filter_by(id_evento).first() is None:
            return 'Evento no existe existe', 400
        evento = Evento.query.get_or_404(id_evento)

        db.session.delete(evento)

        db.session.commit()

        return 'Evento Eliminado', 204

class Usuario(Resource):
    def post(self):
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        user = User.query.filter_by(username=username).first()
        if user is not None:
            return 'Usuario ya existe', 400

        user = User.query.filter_by(email=email).first()
        if user is not None:
            return 'Email de Usuario ya existe', 400

        user_data = User(username=username, email=email )
        user_data.set_password(password)
        db.session.add(user_data)
        db.session.commit()
        return 'Usuario creado', 204

api.add_resource(EventosPorUsuario, '/api/usuario/eventos/<int:id_usuario>')

api.add_resource(Eventos, '/api/eventos/')

api.add_resource(PorEvento,'/api/evento/<int:id_evento>')

api.add_resource(Usuario,'/api/usuario/')