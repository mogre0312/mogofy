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
    colors = db.relationship('Color', secondary=product_color, backref='products')
    sizes = db.relationship('Size', secondary=product_size, backref='product')
    

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
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
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
            'price':product.price,
            'colors':[x.title for x in product.colors],
            'sizes':[x.title for x in product.sizes]
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

@app.route('/colors/<int:id>', methods =['PUT', 'PATCH'])
def update_color(id):
    payload = request.json
    title = payload.get('title', '')
    color = Color.query.filter_by(id=id).first()
    
    if color is not None:
        color.title = title
        db.session.commit()
        return 'Color updated'
    else:
        return 'Color not found' 


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

@app.route('/size/<int:id>', methods =['PUT', 'PATCH'])
def update_size(id):
    payload = request.json
    title = payload.get('title', '')
    size = Size.query.filter_by(id=id).first()
    
    if size is not None:
        size.title = title
        db.session.commit()
        return 'Size updated'
    else:
        return 'Size not found'
    

@app.route('/colors_on_product', methods =['POST'])
def colors_on_product():
    payload = request.json
    product_id = payload.get('product_id','')
    colors = payload.get('colors','')
    
    product = Product.query.filter_by(id=product_id).first()
    for x in colors:
        color = Color.query.filter_by(id=x).first()
        #if color is not found in database, do not append
        if color is not None:
            product.colors.append(color)
        
    db.session.commit()
    return 'Colors attached'

@app.route('/sizes_on_product', methods=['POST'])
def sizes_on_product():
    payload= request.json
    product_id = payload.get('product_id','')
    sizes = payload.get('sizes_id','')
    
    product = Product.query.filter_by(id=product_id).first()
    for x in sizes:
        size = Size.query.filter_by(id=1).first()
        if size is not None:
            product.sizes.append(size)
            
    db.session.commit()
    return 'Sizes attached'


@app.route('/orders', methods = ['POST'])
def create_order():
    payload = request.json
    user_id = payload.get('user_id', '')
    products = payload.get('products', [])
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return 'User not found'
    
    total = 0.0
    for item in products:
        product = Product.query.filter_by(id=item['product_id']).first()
        # product is found
        if product is not None:
              total += product.price * item['quantity']
    
    #adding order          
    order = Order(
        user_id = user_id,
        total = total
    )
    db.session.add(order)
    db.session.commit()  
    
    # adding order_items
    for item in products:
        order_item = Order_Item(
            order_id = order.id,
            product_id = item['product_id'],
            quantity = item['quantity'],
            color_id = item['color_id'],
            size_id = item['size_id']
        )
        db.session.add(order_item)
    
    db.session.commit()  
    
    return 'Order Created'

@app.route('/orders/<int:id>', methods = ['GET'])
def show_order(id):
    order = Order.query.filter_by(id=id).first()
    
    if order is None:
        return 'Order not found'
    else:
        order_items = Order_Item.query.filter_by(order_id=id).all()
        print(order_items)
        items = []
        for x in order_items:
            items.append({
                'product_id':x.product_id,
                'quantity':x.quantity,
                'color_id':x.color_id,
                'size_id':x.size_id
            })
        return {
            'user_id':order.user_id,
            'total':order.total,
            'ordered_at':order.ordered_at,
            'items':items
        }
                
if __name__ == 'main':
    app.run(debug=True)