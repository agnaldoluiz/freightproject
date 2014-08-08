from flask import render_template, url_for, redirect, session, g, flash, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from datetime import date
from forms import LoginForm, UserForm, CarrierForm
from config import EVALUATE_PER_PAGE
from models import User, ROLE_USER, ROLE_ADMIN, Carrier, Invoice, Freight, Hawb, Shipper, Recipient, Service

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
@app.route('/main')
@login_required
def index():
	user = g.user
	freights = Freight.query.all()
	evaluate = []
	approved = []
	processed = []
	dispute = []
	for freight in freights:
		if freight.status == 'E':
			evaluate.append(freight)
		elif freight.status == 'A':
			approved.append(freight)
		elif freight.status == 'P':
			processed.append(freight)
		elif freight.status == 'D':
			dispute.append(freight)


	return render_template("main.html",
		approved = approved,
		processed = processed,
		evaluate = evaluate,
		freights = freights)

@app.route('/evaluate')
@app.route('/evaluate/<int:page>')
def evaluate(page = 1):
	return render_template("evaluate.html")

@app.route('/dispute')
def dispute():
	return 'Hello World!'


@app.route('/login', methods = ['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.is_submitted():
		if form.validate_on_submit():
			session['remember_me'] = form.remember_me.data
			print form.email.data				
			user = User.query.filter_by(email = form.email.data).first()
			if user is None:
				flash('User not registered')
				return redirect(url_for('login'))
			remember_me = False
			if 'remember_me' in session:
				remember_me = session['remember_me']
				session.pop('remember_me', None)
			login_user(user, remember = remember_me)
			return redirect(request.args.get('next') or url_for('index'))
		else:
			flash('Invalid login. Please try again.')
			return redirect(url_for('login'))
	return render_template('login.html',
		form = form)

@app.route('/logout')
def logout():
    logout_user()
    flash('User logged out')
    return redirect(url_for('login'))

@app.route('/data')
@login_required
def data():
	input_file = open("data.csv", "r+")
	csv_all = input_file.read()
	csv_lines = csv_all.split('\n')
	data = []
	for line in csv_lines:	data.append(line.split(','))
	input_file.close()
	return render_template('data.html',
		data = data)

@app.route('/carriers')
@login_required
def carriers():
	carriers = Carrier.query.all()
	return render_template('carriers.html',
		carriers = carriers)

@app.route('/carrier/<name>')
@login_required
def carrier(name):
	carrier = Carrier.query.filter_by(name = name).first()
	return render_template('carrier.html',
		carrier = carrier)

@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin():
	#New User Done. To do: estatistics
	if g.user.role is not ROLE_ADMIN:
		flash('You need to be an administrator to access this page')
		return redirect(url_for('index'))
	form = UserForm()
	carrier_form = CarrierForm()
	role = 0
	if form.is_submitted():
		if form.validate_on_submit():
			user = User.query.filter_by(email = form.email.data).first()
			if user is None:
				user = User(email = form.email.data, password = form.new_password.data, role = role)
				db.session.add(user)
				db.session.commit()
				flash('User created. Logout to login as the new user')
			else:
				flash('User already exists')
		else:
			flash('Form not valid. Fill it up again')
		return redirect(url_for('admin'))
	if carrier_form.is_submitted():
		if carrier_form.validate_on_submit():
			carrier = Carrier.query.filter_by(name = form.name.data).first()
			if carrier is None:
				carrier = Carrier(name = form.name.data, dispute_emails = form.dispute_emails.data, payment_release_emails = form.payment_release_emails.data)
				db.session.add(carrier)
				db.session.commit()
				flash('Carrier created')
			else:
				flash('This carrier already exists')
		return redirect(url_for('carriers'))
	return render_template('admin.html',
		form = form,
		carrier_form = carrier_form,
		role = role)

@app.route('/admin/users/')
@login_required
def user_admin():
	if g.user.role is not ROLE_ADMIN:
		flash('You need to be an administrator to access this page')
		return redirect(url_for('index'))
	users = User.query.all()
	return render_template('users.html',
		users = users)

@app.route('/user/<name>')
@login_required
def user(name):
	email = name + '@embraer.com'
	user = User.query.filter_by(email = email).first()
	return render_template('user.html',
		user = user)

@app.route('/upload')
def upload():
	input_file = open("data.csv", "r+")
	csv_all = input_file.read()
	csv_lines = csv_all.split('\n')
	data = []
	for line in csv_lines:	
		data.append(line.split(','))
	input_file.close()

	def monthToNum(date):

		return {
	        'Jan' : 1,
	        'Feb' : 2,
	        'Mar' : 3,
	        'Apr' : 4,
	        'May' : 5,
	        'Jun' : 6,
	        'Jul' : 7,
	        'Aug' : 8,
	        'Sep' : 9, 
	        'Oct' : 10,
	        'Nov' : 11,
	        'Dec' : 12
		}[date]

	def addZeros(number):
		new_number = ''
		if int(number) < 10:
			new_number = '0' + number
			return new_number
		else:
			return number

	def validDateInvoice(string):
		listing = string.split('-')
		listing[2] = '20' + listing[2]
		listing[2] = int(listing[2])
		listing[1] = monthToNum(listing[1])
		listing[0] = int(listing[0])
		date_obj = date(listing[2], listing[1], listing[0])
		return date_obj

	def validDateShip(string):
		listing = string.split('/')
		new_date = date(int(listing[2]), int(listing[0]), int(listing[1]))
		return new_date

	def id_invoice_and_hawb(string):
		invoice = string.split('#')[1]
		return int(invoice)

	def validEntryNumber(number):
		if number is not None:
			num = number.split('\'')[1]
			return int(num)
		else:
			return number

	def validEntryDate(string):
		listing = string.split(' ')[2]
		year = ''
		for i in range(4):
			year += listing[i]
		year = int(year)
		new_date = date(year, int(listing[4] + listing[5]), int(listing[6] + listing[7]))
		return new_date

	#Carrier Code: 44
	for i in range(len(csv_lines)):
		invoice = Invoice(id = id_invoice_and_hawb(data[i][1]), date = validDateInvoice(data[i][2]), bill_to_account = int(data[i][16]) , total = float(data[i][3]), carrier_id = int(data[i][44]))
		hawb = Hawb(id = id_invoice_and_hawb(data[i][7]), total = float(data[i][10]), frt = float(data[i][11]), gov = float(data[i][12]), ins = float(data[i][13]), fuel = float(data[i][14]), other = float(data[i][15]), char_weight = float(data[i][9]), ent_weight = float(data[i][8]))
		shipper = Shipper(company = str(data[i][18]), name = str(data[i][19]) , zip_code = str(data[i][20]), city = str(data[i][21]), state = str(data[i][22]) , country = str(data[i][23]), classification = int(data[i][39]))
		recipient = Recipient(company = str(data[i][25]), name = str(data[i][24]), zip_code = str(data[i][26]), city = str(data[i][27]), state = str(data[i][28]) , country = str(data[i][29]), classification = int(data[i][40]))
		service = Service(name = str(data[i][4]), carrier_id = str(data[i][44]))
		freight = Freight(ship_date = validDateShip(data[i][5]), entry = int(data[i][6]), entry_date = validEntryDate(data[i][33]), payor = str(data[i][17]), reference = str(data[i][30]), other_cost = str(data[i][31]), canada_tax = float(data[i][32]), delivery_date = validDateInvoice(data[i][35]), first_upload_date = validDateInvoice(data[i][34]), status = str(data[i][36]), invoice_id = invoice.id, service_id = service.id, hawb_id = hawb.id, shipper_id = shipper.id, recipient_id = recipient.id, user_id = g.user.id) 

		db.session.add(invoice)
		db.session.add(hawb)
		db.session.add(shipper)
		db.session.add(recipient)
		db.session.add(service)
		db.session.add(freight)

		db.session.commit()

		flash('The freight was added %s' % (freight.ship_date))
	return redirect(url_for('index'))