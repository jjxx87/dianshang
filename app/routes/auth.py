from flask import Blueprint, render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码无效', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            if user.is_merchant:
                next_page = url_for('merchant.dashboard')
            else:
                next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='登录', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        is_merchant = form.role.data == 'merchant'
        user = User(username=form.username.data, email=form.email.data, is_merchant=is_merchant)
        user.set_password(form.password.data)
        
        if is_merchant:
            user.store_name = form.store_name.data or f"{user.username}的小店"
            
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='注册', form=form)
