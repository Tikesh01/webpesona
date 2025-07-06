from flask_sqlalchemy import SQLAlchemy

# Only create the db instance, do not create Flask app here
db = SQLAlchemy()

# User model for registration/signin/up
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(200))
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<User {self.__dict__}>'