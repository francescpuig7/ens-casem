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
from app import app, lm, db, bc, session
from app.models import User, Comentari, Invitat
from app.forms import LoginForm, RegisterForm, AllergiesForm, CreateInvitatForm

MAP_ESPECIE = {'1': 'Pepe', '2': 'Sale'}
MAP_CONFIRMAT = {'on': True, 'off': False}


@app.route('/language=<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(url_for('index'))


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Logout user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/<lang_code>/cerimonia', methods=['GET'])
def monestir(lang_code):
    lang = lang_code
    if lang != get_language():
        set_language(lang)
    return render_template(f'pages/{lang}/monestir.html')


@app.route('/<lang_code>/apat', methods=['GET'])
def restaurant(lang_code):
    lang = lang_code
    if lang != get_language():
        set_language(lang)
    return render_template(f'pages/{lang}/restaurant.html')


@app.route('/<lang_code>/comentaris', methods=['GET'])
def get_comentaris(lang_code):
    comentaris = Comentari.query.all()
    lang = lang_code
    if lang != get_language():
        set_language(lang)
    return render_template(f'pages/{lang}/comentaris.html', comentaris=comentaris)


@app.route('/comentaris')
def download_comentaris():
    try:
        comentaris = Comentari.query.all()
        df = pd.DataFrame()
        for comentari in comentaris:
            df = df.append([{
                'Nome/Nomi': comentari.nom,
                'Conferma': comentari.confirmat,
                'Allergie/Intoleranze': comentari.allergies,
                'Comentari': comentari.comentari,
                'Seggiolino': comentari.trona
            }])
        filename = 'Elenco_informazioni.csv'
        df.to_csv(os.path.join(app.root_path, 'static', filename), sep=';', index=False)
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)
    except Exception as err:
        return render_template('pages/error-500.html', msg=err)


@app.route('/<lang_code>/form_comentaris', methods=['GET', 'POST'])
def post_comentaris(lang_code):
    form = AllergiesForm(request.form)

    lang = lang_code
    if lang != get_language():
        set_language(lang)
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '', type=str)
            bus = request.form.get('bus', '', type=str)
            allergies = request.form.get('allergies', '', type=str)
            trona = request.form.get('trona', '', type=str)
            comentari = request.form.get('comentaris', '', type=str)
            confirmat = request.form.get('confirmat', '', type=str)
            com = Comentari(nom, bus, trona, comentari, confirmat, allergies)
            com.save()
            return render_template(f'pages/{lang}/notificacio_ok.html', form=form)
        except Exception as err:
            print(err)
            return render_template(f'pages/{lang}/error-info.html')
    if request.method == 'GET':
        return render_template(f'pages/{lang}/form_comentaris.html', form=form)


@app.route('/<lang_code>/notificacio_ok', methods=['GET', 'POST'])
def notificacio(lang_code):
    lang = lang_code
    return render_template(f'pages/{lang}/notificacio_ok.html')


@app.route('/invitats', methods=['GET', 'POST'])
def invitats():
    form = CreateInvitatForm(request.form)

    if request.method == 'GET':
        invitats = Invitat.query.all()
        try:
            confirmats = len([x for x in invitats if x.confirmat_ok])
        except Exception as err:
            confirmats = 0
        return render_template(f'pages/invitats.html', invitats=invitats, form=form, confirmats=confirmats)
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '', type=str)
            sexe = request.form.get('sexe', 'M', type=str)
            especie = request.form.get('especie', '1', type=str)
            confirmat = request.form.get('confirmat', 'off')
            comentaris = request.form.get('comentaris', '')
            c = Invitat(nom=nom, sexe=sexe, especie=MAP_ESPECIE[especie], confirmat=MAP_CONFIRMAT[confirmat],
                        notes=comentaris)
            c.save()
            invitats = Invitat.query.all()
            try:
                confirmats = len([x for x in invitats if x.confirmat_ok])
            except Exception as err:
                confirmats = 0
            return render_template(f'pages/invitats.html', invitats=invitats, form=form, confirmats=confirmats)
        except Exception as err:
            print(err)
            return render_template('pages/error-404.html')


@app.route("/form_update_invitat", methods=["POST"])
def form_update_invitat():
    if request.method == 'POST':
        invitat_id = request.form.get("id")
        invitat = Invitat.query.filter_by(id=invitat_id).first()
        return render_template('pages/it/update_invitat.html', item=invitat)


@app.route("/update_invitat", methods=["POST"])
def update_invitat():
    if request.method == 'POST':
        try:
            print(request.form)
            invitat_id = request.form.get("id")
            invitat = Invitat.query.filter_by(id=invitat_id).first()

            nom = request.form.get('nom', '', type=str)
            sexe = request.form.get('sexe', '', type=str)
            especie = request.form.get('especie', '', type=str)
            confirmat = request.form.get('confirmat', 'off')
            comentaris = request.form.get('notes', '')

            invitat.nom = nom
            invitat.sexe = sexe
            invitat.especie = MAP_ESPECIE[especie]
            invitat.confirmat = confirmat
            invitat.notes = comentaris

            db.session.commit()
            return redirect(url_for('invitats'))
        except Exception as err:
            print(err)
            return render_template('pages/error-404.html')


@app.route('/coses', methods=['GET'])
def get_coses():
    return render_template('pages/coses.html')


@app.route('/<lang_code>/cancons', methods=['GET'])
def get_cancons(lang_code):
    lang = lang_code
    if lang != get_language():
        set_language(lang)
    return render_template(f'pages/{lang}/cancons.html')


# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)
    msg = None

    if request.method == 'GET':
        return render_template('accounts/register.html', form=form, msg=msg)

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

    # try to match the pages defined in -> pages/<input file>
    if path == 'it':
        set_language('it')
        path = 'index.html'
    lang = get_language()
    if path in ('ca', 'it') or path != 'index.html':
        path = 'index.html'
    try:
        return render_template(f'pages/{lang}/'+path)
    except Exception as err:
        print(err)
        return render_template('pages/error-404.html')


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


@app.route('/<lang_code>/gallery')
def gallery(lang_code):
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


def get_language():
    return session.get('language', 'ca')


# Escrits
@app.route('/ca/anna-ngnkndcw', methods=['GET'])
def anna_puig():
    return render_template(f'pages/ca/escrits/anna-ngnkndcw.html')


@app.route('/it/tellicherrymikvnhjm', methods=['GET'])
def tellicherrymikvnhjm():
    return render_template(f'pages/it/scritti/tellicherrymikvnhjm.html')


@app.route('/it/tellicherrydvideaccvm', methods=['GET'])
def tellicherrydvideaccvm():
    return render_template(f'pages/it/scritti/tellicherrydvideaccvm.html')


@app.route('/it/tellicherryolekseushu', methods=['GET'])
def tellicherryolekseushu():
    return render_template(f'pages/it/scritti/tellicherryolekseushu.html')
