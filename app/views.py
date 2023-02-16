# -*- encoding: utf-8 -*-
"""
License: CCA 3.0 License
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging
import pandas as pd

# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort

# App modules
from app import app, lm, db, bc
from app.models import User, Comentari, Invitat
from app.forms import LoginForm, RegisterForm, AllergiesForm


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Logout user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/cerimonia', methods=['GET'])
def monestir():
    return render_template('pages/monestir.html')


@app.route('/apat', methods=['GET'])
def restaurant():
    return render_template('pages/restaurant.html')


@app.route('/comentaris', methods=['GET'])
def get_comentaris():
    comentaris = Comentari.query.all()
    return render_template('pages/comentaris.html', comentaris=comentaris)


#todo: encara no funciona
@app.route('/comentaris', methods=['GET', 'POST'])
def download_comentaris():
    comentaris = Comentari.query.all()
    df = pd.DataFrame()
    for comentari in comentaris:
        df.append({'Nom': comentari.nom, 'Comentari': comentari.comentari, 'Trones': comentari.numero_trona})
    filename = '{0}_{1}_.csv'.format("Llistat_comentaris", str(os.getuid()))
    df.to_csv('./uploads' + filename, sep=';')
    uploads = './uploads'
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/form_comentaris', methods=['GET', 'POST'])
def post_comentaris():
    form = AllergiesForm(request.form)

    if request.method == 'POST':
        nom = request.form.get('nom', '', type=str)
        bus = request.form.get('bus', '', type=str)
        trona = request.form.get('trona', '', type=str)
        comentari = request.form.get('comentaris', '', type=str)
        com = Comentari(nom, bus, trona, comentari)
        com.save()
        return render_template('pages/notificacio_ok.html', form=form)
    if request.method == 'GET':
        return render_template('pages/form_comentaris.html', form=form)


@app.route('/notificacio_ok', methods=['GET', 'POST'])
def notificacio():
    return render_template('pages/notificacio_ok.html')


@app.route('/elements_bckup', methods=['GET'])
def elements():
    import pandas as pd
    df = pd.read_csv("invitatsd.csv", delimiter=';')
    df = df.fillna(0)
    db.session.delete(Invitat)
    print(df)
    for elem in df.T.to_dict().values():
        if elem['pepe'] == 1.0:
            sexe = 'H'
            especie = 'Pepe'
        else:
            sexe = 'D'
            especie = 'Sale'
        confirmat = False
        print(elem)
        if int(elem['Confirmados']) == 1:
            confirmat = True

        c = Invitat(nom=elem['Nomi'], sexe=sexe, especie=especie, confirmat=confirmat)
        print(c)
        c.save()
    return render_template('pages/elements_bckup.html')


@app.route('/invitats', methods=['GET'])
def get_invitats():
    invitats = Invitat.query.all()
    return render_template('pages/invitats.html', invitats=invitats)


# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)
    msg = None

    if request.method == 'GET':
        return render_template('accounts/register.html', form=form, msg=msg )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)

        # Get usuaris per nom
        user = User.query.filter_by(user=username).first()
        # Get usuaris per email
        user_by_email = User.query.filter_by(email=email).first()
        if user or user_by_email:
            msg = 'Error: User ja existent!'
        else:
            pw_hash = password
            user = User(username, email, pw_hash)
            user.save()
            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'

    else:
        msg = 'Input error'

    return render_template('accounts/register.html', form=form, msg=msg)


# Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Password incorrecte"
        else:
            msg = "Usuari no trobat"

    return render_template('accounts/login.html', form=form, msg=msg)


# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    if not current_user.is_authenticated:
        pass
        #return redirect(url_for('login'))

    content = None

    #try:

    # try to match the pages defined in -> pages/<input file>
    return render_template('pages/'+path )
    
    #except:
    #    
    #    return render_template( 'pages/error-404.html' )

# Return sitemap 
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')


# Image Gallery
import glob
import sys
import binascii


def encode(x):
    return binascii.hexlify(x.encode('utf-8')).decode()


def decode(x):
    return binascii.unhexlify(x.encode('utf-8')).decode()


app.config['IMAGE_EXTS'] = [".png", ".jpg", ".jpeg", ".gif", ".tiff"]


@app.route('/gallery')
def gallery():
    root_dir = os.path.join(os.getcwd(), 'app', 'static', 'gallery')
    image_paths = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in app.config['IMAGE_EXTS']):
                image_paths.append(encode(os.path.join(root, file)))
    return render_template('gallery/gallery.html', paths=image_paths)


@app.route('/cdn/<path:filepath>')
def download_file(filepath):
    dir, filename = os.path.split(decode(filepath))
    return send_from_directory(dir, filename, as_attachment=False)