# -*- encoding: utf-8 -*-
"""
License: CCA 3.0 License
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, IntegerField, BooleanField, RadioField
from wtforms.validators import InputRequired, Email, DataRequired


class LoginForm(FlaskForm):
	username = StringField(u'Username', validators=[DataRequired()])
	password = PasswordField(u'Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
	name = StringField(u'Name')
	username = StringField(u'Username', validators=[DataRequired()])
	password = PasswordField(u'Password', validators=[DataRequired()])
	email = StringField(u'Email', validators=[DataRequired(), Email()])


class AllergiesForm(FlaskForm):
	nom = StringField(u'Nom', validators=[DataRequired()])
	confirmat_si = RadioField(u'Confirmat Si')
	confirmat_no = RadioField(u'Confirmat No')
	allergies = StringField('Allergies')
	trona = StringField('Trona')
	comentaris = TextAreaField(u'Comentaris')


class CreateInvitatForm(FlaskForm):
	nom = StringField(u'Nom', validators=[DataRequired()])
