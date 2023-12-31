    # -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import ssl

import nltk
from decouple import config

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3' + '?check_same_thread=False')
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://u262389223_brontomind:Summer321@srv865.hstgr.io/u262389223_brontomind'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Demo configurations
    DEMO_KEY = config('DEMO_KEY', default='DEMO')

    # System modules
    PREDICTION_MODULE = '7'
    FORECASTING_MODULE = '8'
    ROBOTIC_MODULE = '9'
    CLASSIFICATION_MODULE = '10'
    FILES_CLASSIFICATION_MODULE = '11'
    CLUSTERING_MODULE = '13'


class ProductionConfig(Config):
    DEBUG = True

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE', default='postgresql'),
        config('DB_USERNAME', default='appseed'),
        config('DB_PASS', default='pass'),
        config('DB_HOST', default='localhost'),
        config('DB_PORT', default=5432),
        config('DB_NAME', default='appseed-flask')
    )


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
