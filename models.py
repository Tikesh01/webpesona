from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

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
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    p_title = db.Column(db.String(50), nullable=False)
    p_description = db.Column(db.String(), nullable=False)
    p_price = db.Column(db.Float(), nullable=False)
    p_amount = db.Column(db.Float(), nullable=False)
    p_special = db.Column(db.String(), nullable=False)
    

class Web(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    templates = db.relationship('Template', backref='owner', lazy=False)
    header_pages = db.relationship('Header_page',backref='owner', lazy=False )
    is_content_editable = db.Column(db.Boolean, default = False)
    preview_page  = db.Column(db.String(100), default="home.html")

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    web_id = db.Column(db.Integer, db.ForeignKey('web.id'), nullable=False)
    
class Header_page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    web_id = db.Column(db.Integer, db.ForeignKey('web.id'), nullable=False)
    