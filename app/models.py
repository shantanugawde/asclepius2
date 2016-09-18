from werkzeug.security import generate_password_hash, check_password_hash
from app import db


conditionhistory = db.Table('conditionhistory',
	db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
	db.Column('condition_id', db.String, db.ForeignKey('conditions.id'))
)

class User(db.Model):
	__tablename__ = 'users'
	
	id = db.Column(db.Integer, primary_key=True)
	#password_hash = db.Column(db.String(128))
	email = db.Column(db.String(120), index=True, unique=True)
	name = db.Column(db.String(120))
	age = db.Column(db.Integer)
	gender = db.Column(db.String(120))
	condtions = db.relationship('Condition',
				secondary=conditionhistory,
				primaryjoin=(conditionhistory.c.user_id == id),
				secondaryjoin=(conditionhistory.c.condition_id == id),
				backref=db.backref('users', lazy='dynamic'),
				lazy='dynamic')
	
	def __repr__(self):
		return '<User %r>' % (self.name)
	
	#@property
	#def password(self):
	#	raise AttributeError('password is not a readable attribute')
	
	#@password.setter
	#def password(self, password):
	#	self.password_hash = generate_password_hash(password)
		
	#def verify_password(self, password):
	#	return check_password_hash(self.password_hash, password)
		

class Symptom(db.Model):
	__tablename__ = 'symptoms'
	
	id = db.Column(db.String(30), primary_key=True)
	label = db.Column(db.String(360), unique=True)
	
	def __repr__(self):
		return '<Symptom %r>' % (self.label)
	
class Condition(db.Model):
	__tablename__ = 'conditions'
	
	id = db.Column(db.String(30), primary_key=True)
	name = db.Column(db.String(360), primary_key=True)

	def __repr__(self):
		return '<Condition %r>' % (self.name)
