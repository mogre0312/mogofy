from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mogofy.db"
db.init_app(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime,  nullable=True)
    
class Product(db.Model):
    __tablename__='product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    

class Coupon(db.Model):
    __tablename__='coupon'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(10), nullable=True)
    discount = db.Column(db.Integer, default=0)
    

class Color(db.Model):
    __tablename__='color'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)
    
    
class Size(db.Model):
    __tablename__='size'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)
    

class Order(db.Model):
    __tablename__='order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    coupon_code = db.Column(db.String(10), nullable=False)
    total = db.Column(db.Float(precision=2), default = 0)
    order_date = db.Column(db.DateTime, default=datetime.date)
    order_time = db.Column(db.DateTime, default=datetime.time)
    cancelled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Order_Item(db.Model):
    __tablename__='order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    color_id = db.Column(db.Integer, db.ForeignKey('color.id'))
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'))


with app.app_context():
    db.create_all()
    
    
if __name__ == 'main':
    app.run(debug=True)