from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem
from app.forms import ProductForm

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
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            image_url=form.image_url.data,
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
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.image_url = form.image_url.data
        db.session.commit()
        flash('商品已更新！', 'success')
        return redirect(url_for('merchant.dashboard'))
    return render_template('merchant/edit_product.html', title='编辑商品', form=form, product=product)

@bp.route('/product/<int:id>/delete', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    if product.merchant_id != current_user.id:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('商品已删除。', 'success')
    return redirect(url_for('merchant.dashboard'))
