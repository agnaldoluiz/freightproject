from app import app
from app import db, models
admin = models.User(email = 'admin@embraer.com', password = 'FirstPassword', role = models.ROLE_ADMIN)
walter = models.User(email = 'walter@embraer.com', password = 'Wally', role = models.ROLE_USER)
db.session.add(admin)
db.session.add(walter)
db.session.commit()