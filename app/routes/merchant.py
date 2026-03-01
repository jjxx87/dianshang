import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem
from app.forms import ProductForm
from sqlalchemy.exc import IntegrityError

bp = Blueprint('merchant', __name__)

@bp.before_request
def check_merchant():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    if not current_user.is_merchant:
        flash('只有商户可以访问此页面。', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/dashboard')
def dashboard():
    products = Product.query.filter_by(merchant_id=current_user.id).all()
    # 查找包含当前商户商品的订单
    orders = Order.query.join(Order.items).join(OrderItem.product).filter(Product.merchant_id == current_user.id).distinct().all()
    # Actually, orders contain items from multiple merchants. Need to think about this.
    # A simpler approach: Just show products for now.
    return render_template('merchant/dashboard.html', title='商户中心', products=products)

@bp.route('/product/new', methods=['GET', 'POST'])
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            f = form.image.data
            filename = secure_filename(f.filename)
            # Ensure unique filename
            filename = f"{uuid.uuid4().hex}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            f.save(upload_path)
            image_url = f"uploads/{filename}"

        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            image_url=image_url,
            merchant_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('商品已创建！', 'success')
        return redirect(url_for('merchant.dashboard'))
    return render_template('merchant/edit_product.html', title='添加商品', form=form)

@bp.route('/product/<int:id>/edit', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if product.merchant_id != current_user.id:
        abort(403)
    
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        if form.image.data:
            f = form.image.data
            filename = secure_filename(f.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            f.save(upload_path)
            product.image_url = f"uploads/{filename}"

        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        db.session.commit()
        flash('商品已更新！', 'success')
        return redirect(url_for('merchant.dashboard'))
    return render_template('merchant/edit_product.html', title='编辑商品', form=form, product=product)

@bp.route('/product/<int:id>/delete', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    if product.merchant_id != current_user.id:
        abort(403)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('商品已删除。', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('无法删除该商品，因为它已被包含在订单中。', 'danger')
    return redirect(url_for('merchant.dashboard'))

@bp.route('/orders')
@login_required
def orders():
    # 查找包含当前商户商品的订单
    orders = Order.query.join(Order.items).join(OrderItem.product).filter(Product.merchant_id == current_user.id).distinct().all()
    return render_template('merchant/orders.html', title='订单管理', orders=orders)

@bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    # 检查该订单是否包含当前商户的商品
    items = OrderItem.query.join(OrderItem.product).filter(OrderItem.order_id == order_id, Product.merchant_id == current_user.id).all()
    
    if not items:
        abort(403) # 不属于该商户的订单
        
    total_amount = sum(item.price * item.quantity for item in items)
    
    return render_template('merchant/order_detail.html', title='订单详情', order=order, items=items, total_amount=total_amount)

@bp.route('/ship_item/<int:item_id>', methods=['POST'])
@login_required
def ship_item(item_id):
    item = OrderItem.query.get_or_404(item_id)
    # 检查商品是否属于当前商户
    if item.product.merchant_id != current_user.id:
        abort(403)
        
    item.status = 'shipped'
    db.session.commit()
    flash('商品状态已更新为已发货。', 'success')
    return redirect(url_for('merchant.order_detail', order_id=item.order_id))
