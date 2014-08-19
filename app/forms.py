from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, SelectField, TextAreaField
from wtforms.validators import Required, EqualTo, Length

class LoginForm(Form):
    email = TextField('Email', validators = [Required()])
    password = PasswordField('Password', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class UserForm(Form):
	email = TextField('Email', validators = [Required(), Length(min=6, max=35)])
	new_password = PasswordField('Password', validators = [Required(), EqualTo('confirm_password', message='Passwords must match')])
	confirm_password = PasswordField('Repeat Password', validators = [Required()])

class CarrierForm(Form):
	name = TextField('Name', validators = [Required()])
	dispute_emails = TextAreaField('Dispute Emails')
	payment_release_emails = TextAreaField('Payment Release Emails')

class EvaluateForm(Form):
    pc = SelectField('Profit Center', choices=[('COMPEC', 'COMPEC'), ('COMPOL', 'COMPOL'), ('COMGAR', 'COMGAR'), ('DEFPEC', 'DEFPEC'), ('DEFPOL', 'DEFPOL'), ('DEFGAR', 'DEFGAR'), ('EXEPEC', 'EXEPEC'), ('EXETLC', 'EXETLC'), ('EXEGAR', 'EXEGAR')])