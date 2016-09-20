from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from flask_login import UserMixin

conditionhistory = db.Table('conditionhistory',
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                            db.Column('condition_id', db.String, db.ForeignKey('conditions.id'))
                            )

globalhistory = db.Table('globalhistory',
                         db.Column('condition_id', db.Integer, db.ForeignKey('conditions.id')),
                         db.Column('symptom_id', db.Integer, db.ForeignKey('symptoms.id'))
                         )

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, index=True)
    age = db.Column(db.Integer)
    email = db.Column(db.String(120), unique=True, index=True)
    gender = db.Column(db.String(120))
    conditions = db.relationship('Condition',
                                secondary=conditionhistory,
                                backref=db.backref('users', lazy='dynamic'),
                                lazy='dynamic')

    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_condition(self, condition):
        if not self.has_condition(condition):
            self.conditions.append(condition)

    def has_condition(self, condition):
        return self.conditions.filter(conditionhistory.c.condition_id == condition.id).count() > 0

    def get_conditions(self):
        return self.conditions.all()

    def __repr__(self):
        return '<User %r>' % (self.name)


class Symptom(db.Model):
    __tablename__ = 'symptoms'

    id = db.Column(db.String(30), primary_key=True)
    label = db.Column(db.String(360), unique=True)

    def __repr__(self):
        return '<Symptom %r>' % (self.label)


class Condition(db.Model):
    __tablename__ = 'conditions'

    id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(360))
    symptoms = db.relationship('Symptom',
                                 secondary=globalhistory,
                                 backref=db.backref('conditions', lazy='dynamic'),
                                 lazy='dynamic')

    def add_symptom(self, symptom):
        if not self.has_symptom(symptom):
            self.symptoms.append(symptom)

    def has_symptom(self, symptom):
        return self.symptoms.filter(globalhistory.c.symptom_id == symptom.id).count() > 0

    def get_symptoms(self):
        return self.symptoms.all()

    def __repr__(self):
        return '<Condition %r>' % (self.name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
