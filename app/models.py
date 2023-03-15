# -*- encoding: utf-8 -*-
"""
License: CCA 3.0 License
Copyright (c) 2019 - present AppSeed.us
"""

from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):

    id = db.Column(db.Integer,     primary_key=True)
    user = db.Column(db.String(64),  unique = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user = user
        self.password = password
        self.email = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self 


class Comentari(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(64), unique=True)
    bus = db.Column(db.String(128))
    trona = db.Column(db.String(128))
    comentari = db.Column(db.String(2000))
    confirmat = db.Column(db.String(2))
    allergies = db.Column(db.String(256))

    def __init__(self, nom, bus, trona, comentari, confirmat, allergies):

        self.nom = nom
        self.bus = bus
        self.trona = trona
        self.comentari = comentari
        self.confirmat = confirmat
        self.allergies = allergies

    def __repr__(self):
        return f'{self.nom} --> Confirmat? {self.confirmat}, Al·lèrgies: {self.allergies}, Notes --> {self.comentari}'

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self


class Invitat(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50))
    sexe = db.Column(db.String(10))
    confirmat = db.Column(db.String(2))
    especie = db.Column(db.String(5))
    notes = db.Column(db.String(250))

    def __init__(self, nom, sexe, confirmat=False, especie=None, notes=""):
        self.nom = nom
        self.sexe = sexe
        self.confirmat = 'NO'
        if confirmat:
            self.confirmat = 'SI'
        self.especie = especie
        self.notes = notes

    def __repr__(self):
        return str(
            f"""{self.nom} - Confirmat: {self.confirmat}, Especie: {self.especie}, Sexe: {self.sexe}, 
            Comentaris: {self.notes}"""
        )

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self

    @property
    def confirmat_ok(self):
        if self.confirmat == 'SI':
            return True
        else:
            return False
