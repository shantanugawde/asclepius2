import infermedica_api
import os
import googlemaps

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

infermedica_api.configure(app_id='e0e1634e', app_key='3def7d8607bd91e6e52ebc1f9aa0c9bf')
api = infermedica_api.get_api()
gmaps = googlemaps.Client(key='AIzaSyDVK5ynnDSJZ0MWKRYtKZZKhxTMqTg1rl0')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'asclepius.diagnosis@gmail.com'
MAIL_PASSWORD = 'akkdu123'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

WT_CSRF_ENABLED = True
SECRET_KEY = 'development'