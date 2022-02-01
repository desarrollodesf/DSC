from app import app, db, ma, api
from app.models import User, Evento

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Evento': Evento, 'ma' : ma, "api" : api}