import infermedica_api
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

infermedica_api.configure(app_id='e0e1634e', app_key='3def7d8607bd91e6e52ebc1f9aa0c9bf')
api = infermedica_api.get_api()

WT_CSRF_ENABLED = True
SECRET_KEY = 'development'