from flask import Blueprint, render_template
from app.models import Product

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    products = Product.query.all()
    return render_template('index.html', title='首页', products=products)
