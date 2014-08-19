from flask import render_template, url_for, redirect, session, g, flash, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from datetime import date
from flask.ext.wtf import Form
from forms import LoginForm, UserForm, CarrierForm, EvaluateForm
from config import EVALUATE_PER_PAGE
from models import User, ROLE_USER, ROLE_ADMIN, Carrier, Invoice, Freight, Hawb, Shipper, Recipient, Service, ProfitCenter

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
	accepted = []
	released = []
	dispute = []
	acc_dispute = []
	for freight in freights:
		if freight.status == 'A':
			accepted.append(freight)	
		elif freight.status == 'E':
			evaluate.append(freight)			
		elif freight.status == 'P':
			released.append(freight)
		elif freight.status == 'D':
			dispute.append(freight)
		elif freight.sterling == 'R':
			acc_dispute.append(freight)

	return render_template("main.html",
		acc_dispute = acc_dispute,
		accepted = accepted,
		released = released,
		evaluate = evaluate,
		dispute = dispute,
		freights = freights)

@app.route('/evaluate', methods = ['GET', 'POST'])
@app.route('/evaluate/<int:page>')
def evaluate(page = 1):
	form = EvaluateForm()
	evaluate = Freight.query.filter_by(status = 'E').all()
	pc = None

	if form.validate_on_submit():
		pc = ProfitCenter.query.filter_by(name = form.pc.data).first()
		return render_template("evaluate.html",
			evaluate = evaluate,
			form = form,
			pc = pc)

	return render_template("evaluate.html",
		evaluate = evaluate,
		form = form,
		pc = pc)

@app.route('/evaluate/process')
@login_required
def eval_proc(ev1, pc1):
	return "Evaluation Done"

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
	for line in csv_lines:	data.append(line.split('^'))
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
@login_required
def upload():
	input_file = open("data.csv", "r+")
	csv_all = input_file.read()
	csv_lines = csv_all.split('\n')
	data = []
	for line in csv_lines:	
		data.append(line.split('^'))
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
		if number is '':
			return 0
		else:
			return int(number)

	def validEntryDate(string):
		listing = string.split(' ')
		if len(listing) == 3:
			listing = string.split(' ')[2]
			year = ''
			for i in range(4):
				year += listing[i]
			year = int(year)
			new_date = date(year, int(listing[4] + listing[5]), int(listing[6] + listing[7]))
		else:
			new_date = None
		return new_date

	def canada_tax(string):
		if string == '':
			return 0.0
		else:
			return float(string)

	#Carrier Code: 44
	for i in range(1, len(csv_lines) - 1):
		invoice = Invoice.query.filter_by(id = id_invoice_and_hawb(data[i][1])).first()
		if invoice is None:
			invoice = Invoice(id = id_invoice_and_hawb(data[i][1]), date = validDateInvoice(data[i][2]), bill_to_account = int(data[i][16]) , total = float(data[i][3]), carrier_id = int(data[i][44]))
		db.session.add(invoice)
		hawb = Hawb(number = id_invoice_and_hawb(data[i][7]), total = float(data[i][10]), frt = float(data[i][11]), gov = float(data[i][12]), ins = float(data[i][13]), fuel = float(data[i][14]), other = float(data[i][15]), char_weight = float(data[i][9]), ent_weight = float(data[i][8]))
		db.session.add(hawb)
		shipper = Shipper(company = str(data[i][18]), name = str(data[i][19]) , zip_code = str(data[i][20]), city = str(data[i][21]), state = str(data[i][22]) , country = str(data[i][23]), classification = int(data[i][39]))
		db.session.add(shipper)
		recipient = Recipient(company = str(data[i][25]), name = str(data[i][24]), zip_code = str(data[i][26]), city = str(data[i][27]), state = str(data[i][28]) , country = str(data[i][29]), classification = int(data[i][40]))
		db.session.add(recipient)
		service = Service(name = str(data[i][4]), carrier_id = str(data[i][44]))
		db.session.add(service)
		db.session.commit()
		freight = Freight(ship_date = validDateShip(data[i][5]), entry = validEntryNumber(data[i][6]), entry_date = validEntryDate(data[i][33]), payor = str(data[i][17]), reference = str(data[i][30]), other_cost = str(data[i][31]), canada_tax = canada_tax(data[i][32]), delivery_date = validDateInvoice(data[i][35]), first_upload_date = validDateInvoice(data[i][34]), status = str(data[i][36]), evaluation_issue = data[i][46], consistency_issue = data[i][41], doc_type = data[i][42], doc_ref = data[i][43], invoice_id = invoice.id, service_id = service.id, hawb_id = hawb.id, shipper_id = shipper.id, recipient_id = recipient.id, user_id = g.user.id)
		db.session.add(freight)
		db.session.commit()

	flash('All the freights were added')
	return redirect(url_for('index'))

@app.route('/admin/reset')
@login_required
def reset():
	import os, subprocess, sys
	if sys.platform == 'win32':
		remove = 'del'
		bin = 'Scripts'
	else:
		remove = 'rm'
		bin = 'bin'

	print "OK"
	subprocess.call([os.path.join(remove), '-r', 'db_repository/'])
	subprocess.call([os.path.join(remove), 'app.db'])
	subprocess.call([os.path.join('flask', bin, 'python'), 'db_create.py'])
	subprocess.call([os.path.join('flask', bin, 'python'), 'db_migrate.py'])
	print "OK2"
	print "OK2.1"
	'''
	fedex = Carrier(id = 402645, name = 'fedex', dispute_emails = 'kim.robertson@fedex.com; quickresponse7@fedex.com; fedexcollections@fedex.com: fedex.com/us/account/invhome/other/eremit.html' , payment_release_emails = 'kim.robertson@fedex.com; useft@fedex.com; eremit@fedex.com')
	ups_dom = Carrier(id = 402919, name = 'ups_dom', dispute_emails = 'mxarmstrong@ups.com; ajoly@ups.com', payment_release_emails = 'achdetail@ups.com; mxarmstrong@ups.com; ajoly@ups.com')
	ups_imp = Carrier(id = 402623, name = 'ups_imp', dispute_emails = 'preferred.us@ups.com; srbrown@ups.com; ajoly@ups.com', payment_release_emails = 'paymentremit@ups.com; srbrown@ups.com; ajoly@ups.com; kminal@ups.com; WST3XYF@upsstore.com')
	schenker = Carrier(id = 804244, name = 'schenker', dispute_emails = 'kathleen.clarke@dbschenker.com', payment_release_emails = 'kathleen.clarke@dbschenker.com')
	dhl = Carrier(id = 402604, name = 'dhl', dispute_emails = 'henry.leon@dhl.com', payment_release_emails = 'henry.leon@dhl.com')
	mnx = Carrier(id = 807354, name = 'mnx', dispute_emails = 'accounts.receivable@mnx.com', payment_release_emails = 'accounts.receivable@mnx.com')
	sterling = Carrier(id = 402885, name = 'sterling', dispute_emails = 'diane_angus@qintl.com', payment_release_emails = 'diane_angus@qintl.com')
	gzuz = Carrier(id = 805968, name = 'gzuz', dispute_emails = '', payment_release_emails = '')
	db.session.add(fedex)
	db.session.add(ups_dom)
	db.session.add(ups_imp)
	db.session.add(schenker)
	db.session.add(dhl)
	db.session.add(mnx)
	db.session.add(sterling)
	db.session.add(gzuz)
	'''
	admin = User(email = 'admin@embraer.com', role = ROLE_ADMIN, password = 'FirstPassword')
	db.session.add(admin)
	db.session.commit()
	print "OK3"
	return redirect(url_for('admin'))

@app.route('/freights')
@login_required
def freights():
	freights = Freight.query.all()
	accepted = []
	evaluate = []
	for freight in freights:
		if freight.status == 'A':
			accepted.append(freight)
		if freight.status == 'E':
			evaluate.append(freight)
	return render_template('freights.html',
		evaluate = evaluate,
		accepted = accepted,
		freights = freights)

@app.route('/vat_taxes')
@login_required
def vat_taxes():
	ftaxes = []
	freights = Freight.query.all()
	for freight in freights:
		if freight.canada_tax != 0:
			ftaxes.append(freight)
	
	return render_template('vat_taxes.html',
		ftaxes = ftaxes)

@app.route('/vat_taxes/save')
@login_required
def save_vat():
	ftaxes = []
	freights = Freight.query.all()
	for freight in freights:
		if freight.canada_tax != 0:
			ftaxes.append(freight)
	output_file = open("vat_taxes.csv", "w+")
	for ftax in ftaxes:
		output_file.write(str(ftax.service.carrier.name)+',')
		output_file.write(str(ftax.invoice.id)+',')
		output_file.write(str(ftax.invoice.date)+',')
		output_file.write(str(ftax.hawb.number)+',')
		output_file.write(str(ftax.entry)+',')
		output_file.write(str(ftax.entry_date)+',')
		output_file.write(str(ftax.recipient.company)+',')
		output_file.write(str(ftax.recipient.state)+',')
		output_file.write(str(ftax.doc_type)+',')
		output_file.write(str(ftax.doc_ref)+',')		
		output_file.write('\n')
	output_file.close()
	flash('All VAT taxes were saved')
	return redirect(url_for('vat_taxes'))


