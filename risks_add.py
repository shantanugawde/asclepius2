from app import db,models
from config import api
import infermedica_api

r = api.risk_factors_list()
for i in r:
    ri = models.Risk(id = i['id'],name = i['name'])
    db.session.add(ri)
    db.session.commit()