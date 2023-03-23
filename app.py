from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mogofy.db"
db.init_app(app)


product_color= db.Table('product_color',
                        db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
                        db.Column('color_id', db.Integer, db.ForeignKey('color.id'))
                        )

product_size= db.Table('product_size',
                        db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
                        db.Column('size_id', db.Integer, db.ForeignKey('size.id'))
                        )


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
    coupon_code = db.Column(db.String(10), nullable=True)
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

@app.route('/register', methods=['POST'])
def register():
    payload = request.json
    username = payload.get('username')
    password = generate_password_hash(payload.get('password', '')).decode("utf8")
    role = payload.get('role', 'user')
    
    if len(username)>50:
        return 'Username is too long'
    
    user = User(
        username = username,
        password = password,
        role = role
    )
    db.session.add(user)
    db.session.commit()
    return 'User created'

@app.route('/login', methods=['POST'])
def login():
    payload = request.json
    username = payload.get('username', '')
    password = payload.get('password', '')
    user = User.query.filter_by(username=username).first()
    
    if user is None:
        return 'User not found'
    
    if check_password_hash(user.password, password) == True:
        return 'Login Success'
    else:
        return 'Incorrect Password'

@app.route('/products', methods=['POST'])
def add_newproduct():
    payload = request.json
    title = payload.get('title','')
    description = payload.get('description','')
    price = payload.get('price','')

    user = Product(
        title = title,
        description = description,
        price = price
    )

    db.session.add(user)
    db.session.commit()
    return 'Product Added'

@app.route('/products/<int:id>', methods=['GET'])
def show_product(id):
    product = Product.query.filter_by(id=id).first()
    
    if product is None:
        return 'Product not found'
    else:
        return {
            'title': product.title,
            'description':product.description,
            'price':product.price
        }
    
@app.route('/products/<int:id>', methods =['PUT',"PATCH"])
def update_product(id):
    payload = request.json
    title = payload.get('title','')
    description = payload.get('description','')
    price = payload.get('price','')
    product = Product.query.filter_by(id=id).first()
    
    if product is not None:
        product.title= title
        product.description = description
        product.price= price
        db.session.commit()
        return 'Product updated'
    else:
        return 'Product not found'
    

@app.route('/colors', methods=['POST'])
def add_newcolor():
    payload = request.json
    title = payload.get('title','')

    color = Color(
        title = title
    )

    db.session.add(color)
    db.session.commit()
    return 'Color Added'


@app.route('/size', methods=['POST'])
def add_newsize():
    payload = request.json
    title = payload.get('title','')

    size = Size(
        title = title
    )

    db.session.add(size)
    db.session.commit()
    return 'Size Added'

            
    
if __name__ == 'main':
    app.run(debug=True)