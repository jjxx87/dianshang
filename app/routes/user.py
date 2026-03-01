from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem
from app.forms import EditProfileForm

bp = Blueprint('user', __name__)

@bp.before_request
@login_required
def check_login():
    pass

@bp.route('/dashboard')
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/dashboard.html', title='用户中心', orders=orders)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if current_user.is_merchant:
            current_user.store_name = form.store_name.data
        db.session.commit()
        flash('您的个人信息已更新。', 'success')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if current_user.is_merchant:
            form.store_name.data = current_user.store_name
    return render_template('user/profile.html', title='个人信息', form=form)

@bp.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = []
    total_price = 0
    for pid, qty in cart_items.items():
        product = Product.query.get(int(pid))
        if product:
            products.append({'product': product, 'quantity': qty})
            total_price += product.price * qty
    return render_template('user/cart.html', title='购物车', cart_items=products, total_price=total_price)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    pid_str = str(product_id)
    
    if pid_str in cart:
        cart[pid_str] += quantity
    else:
        cart[pid_str] = quantity
    
    session.modified = True
    flash(f'已将 {product.name} 加入购物车', 'success')
    return redirect(url_for('main.index'))

@bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    pid_str = str(product_id)
    if 'cart' in session and pid_str in session['cart']:
        del session['cart'][pid_str]
        session.modified = True
        flash('商品已从购物车移除', 'success')
    return redirect(url_for('user.cart'))

@bp.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('购物车为空', 'warning')
        return redirect(url_for('main.index'))
    
    total_price = 0
    order_items = []
    
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            if product.stock < qty:
                flash(f'商品 {product.name} 库存不足', 'danger')
                return redirect(url_for('user.cart'))
            
            item_price = product.price
            total_price += item_price * qty
            order_items.append((product, qty, item_price))
    
    # Create Order
    order = Order(user_id=current_user.id, total_price=total_price, status='paid') # Assume paid for simplicity
    db.session.add(order)
    db.session.flush() # Get order ID
    
    for product, qty, price in order_items:
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=price)
        product.stock -= qty # Decrease stock
        db.session.add(order_item)
    
    db.session.commit()
    session.pop('cart', None)
    flash('订单已创建！', 'success')
    return redirect(url_for('user.dashboard'))
