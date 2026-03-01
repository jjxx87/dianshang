from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('角色', choices=[('user', '普通用户'), ('merchant', '商户')], default='user')
    store_name = StringField('店铺名称 (仅商户需填)')
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册。')

class ProductForm(FlaskForm):
    name = StringField('商品名称', validators=[DataRequired()])
    description = TextAreaField('商品描述')
    price = FloatField('价格', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('库存', validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField('图片链接')
    submit = SubmitField('提交')

class AddToCartForm(FlaskForm):
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField('加入购物车')
