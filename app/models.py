from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import and_

conditionhistory = db.Table('conditionhistory',
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                            db.Column('condition_id', db.String, db.ForeignKey('conditions.id'))
                            )

globalhistory = db.Table('globalhistory',
                         db.Column('condition_id', db.String, db.ForeignKey('conditions.id')),
                         db.Column('symptom_id', db.String, db.ForeignKey('symptoms.id'))
                         )
riskuser = db.Table('riskuser',
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                    db.Column('risk_id', db.String, db.ForeignKey('risks.id'))
                    )


class UserConditionHistory(db.Model):
    __tablename__ = 'userconditionhistory'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    condition_id = db.Column(db.String, db.ForeignKey('conditions.id'))
    timestamp = db.Column(db.DateTime)
    probability = db.Column(db.Float)
    logged_condition = db.relationship('Condition', backref=db.backref('conditions'))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    email = db.Column(db.String(120), unique=True, index=True)
    gender = db.Column(db.String(120))
    locality = db.Column(db.String(120))
    # conditions = db.relationship('Condition',
    #                              secondary=conditionhistory,
    #                              backref=db.backref('users', lazy='dynamic'),
    #                              lazy='dynamic')

    risks = db.relationship('Risk',
                            secondary=riskuser,
                            backref=db.backref('users', lazy='dynamic'),
                            lazy='dynamic')
    mylog = db.relationship('UserConditionHistory', backref=db.backref('users'), order_by='desc(UserConditionHistory.timestamp)')
    password_hash = db.Column(db.String(128))

    family_id = db.Column(db.Integer, default=0)

    def add_member(self, member):
        if not self.has_family():
            if member.has_family():
                self.family_id = member.family_id
            else:
                self.family_id = self.lastfamily + 1
                member.family_id = self.family_id
        else:
            if not member.has_family():
                member.family_id = self.family_id

    def get_family(self):
        if self.has_family():
            return User.query.filter(self.family_id == User.family_id).all()

    def has_family(self):
        return self.family_id != 0

    @property
    def lastfamily(self):
        return User.query.order_by('id desc').first().id

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # def add_condition(self, condition):
    #     if not self.has_condition(condition):
    #         self.conditions.append(condition)
    #
    # def has_condition(self, condition):
    #     return self.conditions.filter(conditionhistory.c.condition_id == condition.id).count() > 0
    #
    # def get_conditions(self):
    #     return self.conditions.all()

    def add_condition(self, condition, probability):
        if not self.has_condition(condition):
            uc_log = UserConditionHistory(probability=probability, timestamp=datetime.now(), logged_condition=condition)
            self.mylog.append(uc_log)

    def has_condition(self, condition):
        return UserConditionHistory.query.filter(and_(UserConditionHistory.condition_id == condition.id, UserConditionHistory.user_id == self.id)).first() is not None

    def get_conditionlog(self):
        return self.mylog

    def add_risk(self, risk):
        if not self.has_risk(risk):
            self.risks.append(risk)

    def has_risk(self, risk):
        return self.risks.filter(riskuser.c.risk_id == risk.id).count() > 0

    def get_risk(self):
        return self.risks.all()

    def __repr__(self):
        return '<User %r>' % (self.name)


class Symptom(db.Model):
    __tablename__ = 'symptoms'

    id = db.Column(db.String(30), primary_key=True)
    label = db.Column(db.String(360))

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


class Risk(db.Model):
    __tablename__ = 'risks'
    id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(360), unique=True)

    def __repr__(self):
        return '<Risk %r>' % (self.name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
