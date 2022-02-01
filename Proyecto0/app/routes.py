from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Evento, User
from werkzeug.urls import url_parse
from datetime import datetime
import pytz
from tzlocal import get_localzone

@app.route('/')
@app.route('/index')
@login_required
def index():
    events = Evento.query.filter_by(user_id=current_user.id)
    return render_template('index.html', events=events)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/events/<userid>')
@login_required
def events(userid):
    events = Evento.query.filter_by(user_id=userid)
    return render_template('index.html', events=events)



@app.route('/insert/<userid>', methods = ['POST'])
def insert(userid):

    if request.method == 'POST':

        nombre = request.form['nombre']
        lugar = request.form['lugar']
        direccion = request.form['direccion']
        fechaInicio = datetime.strptime(request.form['fechaInicio'],'%Y-%m-%dT%H:%M')
        fechaFin = datetime.strptime(request.form['fechaFin'],'%Y-%m-%dT%H:%M')
        categoria = request.form['categoria']
        evento = request.form['evento']
        fechaCreacion = datetime.strptime(datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/New_York")).strftime('%Y-%m-%dT%H:%M'),'%Y-%m-%dT%H:%M')
        
        my_data = Evento( nombre = nombre, lugar = lugar, direccion = direccion, fechaInicio = fechaInicio, fechaFin = fechaFin, categoria = categoria, evento = evento, fechaCreacion = fechaCreacion, user_id = userid)
        db.session.add(my_data)
        db.session.commit()

        flash("Evento creado exitosamente")
        events = Evento.query.filter_by(user_id=userid)
        return render_template('index.html', events=events)


@app.route('/update', methods = ['GET', 'POST'])
def update():

    if request.method == 'POST':
        my_data = Evento.query.get(request.form.get('id'))

        my_data.nombre = request.form['nombre']
        my_data.lugar = request.form['lugar']
        my_data.direccion = request.form['direccion']
        my_data.fechaInicio = request.form['fechaInicio']
        my_data.fechaFin = request.form['fechaFin']
        my_data.categoria = request.form['categoria']
        my_data.evento = request.form['evento']
        
        db.session.commit()
        flash("Evento actualizado")
        events = Evento.query.filter_by(user_id=my_data.user_id)
        return render_template('index.html', events=events)


@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Evento.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Evento eliminado")

    events = Evento.query.filter_by(user_id=my_data.user_id)
    return render_template('index.html', events=events)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

