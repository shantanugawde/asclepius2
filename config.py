import infermedica_api

infermedica_api.configure(app_id='e0e1634e', app_key='3def7d8607bd91e6e52ebc1f9aa0c9bf')
api = infermedica_api.get_api()

WT_CSRF_ENABLED = True
SECRET_KEY = 'development'