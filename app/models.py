from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    is_merchant = db.Column(db.Boolean, default=False)
    # 商户信息 (如果也是商户)
    store_name = db.Column(db.String(128))
    
    # 关系
    products = db.relationship('Product', backref='merchant', lazy='dynamic')
    orders = db.relationship('Order', backref='buyer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(256))
    merchant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Product {}>'.format(self.name)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending') # pending, paid, shipped, completed
    total_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')

    def __repr__(self):
        return '<Order {}>'.format(self.id)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float) # 购买时的单价

    product = db.relationship('Product')
