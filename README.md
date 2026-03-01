# Flask MySQL 电商系统

这是一个基于 Flask 和 MySQL 的简单电商系统，包含用户模块和商户模块。

## 功能特性

- **用户模块**：注册、登录、浏览商品、加入购物车、下单、查看订单历史。
- **商户模块**：注册（选择商户角色）、登录、商品管理（增删改查）、查看仪表盘。
- **公共模块**：首页商品展示。

## 环境依赖

请确保安装了 Python 3.8+ 和 MySQL 数据库。

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

## 数据库配置

1. 确保 MySQL 服务已启动。
2. 登录 MySQL 并创建数据库 `dianshang_db`：

```sql
CREATE DATABASE dianshang_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 修改 `config.py` 中的数据库连接 URI（如果你的数据库密码不是 `123456`）：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:你的密码@localhost/dianshang_db'
```

## 初始化数据库

运行以下命令创建数据表：

```bash
python init_db.py
```

## 运行项目

```bash
python run.py
```

访问 http://127.0.0.1:5000/

## 使用说明

1. **注册商户**：在注册页面选择“商户”角色，填写店铺名称。
2. **添加商品**：登录商户账号，在商户中心添加商品。
3. **购买商品**：注册普通用户账号，在首页浏览商品，加入购物车并结算。
