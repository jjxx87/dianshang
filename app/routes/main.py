from flask import Blueprint, render_template, request
from app.models import Product

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    products = Product.query.all()
    return render_template('index.html', title='首页', products=products)

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(
            (Product.name.contains(query)) | 
            (Product.description.contains(query))
        ).all()
    else:
        products = []
    return render_template('index.html', title=f'搜索结果: {query}', products=products, search_query=query)
