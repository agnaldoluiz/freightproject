from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class Freight(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
	service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	hawb_id = db.Column(db.Integer, db.ForeignKey('hawb.id'))
	shipper_id = db.Column(db.Integer, db.ForeignKey('shipper.id'))
	recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'))
	ship_date = db.Column(db.Date)
	entry = db.Column(db.Integer)
	entry_date = db.Column(db.Date)
	payor = db.Column(db.String(64))
	reference = db.Column(db.String(128))
	other_cost = db.Column(db.String(128))
	canada_tax = db.Column(db.Integer)
	delivery_date = db.Column(db.Date)
	first_upload_date = db.Column(db.Date)
	status = db.Column(db.String(1))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return "Freight #'%s'" % (str(self.id))

class Carrier(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique = True)
	dispute_emails = db.Column(db.String(512))
	payment_release_emails = db.Column(db.String(512))
	invoices = db.relationship('Invoice', backref = 'carrier', lazy = 'dynamic')
	services = db.relationship('Service', backref = 'carrier', lazy = 'dynamic')

	def __repr__(self):
		return "Carrier '%s'" % self.name
	def avatar(self):
		return '/static/img/' + self.name.lower() + '.jpg'

class Service(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique = False)
	freights = db.relationship('Freight', backref = 'service', lazy = 'dynamic')
	carrier_id = db.Column(db.Integer, db.ForeignKey('carrier.id'))

	def __repr__(self):
		return "Service '%s'" % self.name

class Invoice(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	freights = db.relationship('Freight', backref = 'invoice', lazy = 'dynamic')
	carrier_id = db.Column(db.Integer, db.ForeignKey('carrier.id'))	
	date = db.Column(db.Date)
	total = db.Column(db.Float)
	bill_to_account = db.Column(db.Integer)

	def __repr__(self):
		return "Invoice #'%s'" % self.id

class Hawb(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	number = db.Column(db.Integer)
	freights = db.relationship('Freight', backref = 'hawb', lazy = 'dynamic')
	total = db.Column(db.Float)
	char_weight = db.Column(db.Float)
	ent_weight = db.Column(db.Float)
	frt = db.Column(db.Float)
	gov = db.Column(db.Float)
	ins = db.Column(db.Float)
	fuel = db.Column(db.Float)
	other = db.Column(db.Float)

	def __repr__(self):
		return "HAWB #'%s'" % self.number

class Shipper(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	company = db.Column(db.String(128))
	name = db.Column(db.String(64))
	zip_code = db.Column(db.Integer)
	city = db.Column(db.String(64))
	state = db.Column(db.String(64))
	country = db.Column(db.String(64))
	classification = db.Column(db.Integer)
	freights = db.relationship('Freight', backref = 'shipper', lazy = 'dynamic')

class Recipient(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	company = db.Column(db.String(64))
	zip_code = db.Column(db.Integer)
	city = db.Column(db.String(64))
	state = db.Column(db.String(64))
	country = db.Column(db.String(64))
	classification = db.Column(db.Integer)
	freights = db.relationship('Freight', backref = 'recipient', lazy = 'dynamic')

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(120), index = True, unique = False)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	password = db.Column(db.String(64))
	freights = db.relationship('Freight', backref = 'user', lazy = 'dynamic')

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return self.email.split('@')[0].upper()