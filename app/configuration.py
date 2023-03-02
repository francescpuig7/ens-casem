# -*- encoding: utf-8 -*-
"""
License: CCA 3.0 License
Copyright (c) 2019 - present AppSeed.us
"""

import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():

	LANGUAGES = ['ca', 'it']
	CSRF_ENABLED = True
	SECRET_KEY = "77tgFCdrEEdv77554##@3"
	
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	if os.getenv('ENV', default='TEST') == 'PROD':
		SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
	else:
		SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
