from .database import db

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, nullable=False)
    category = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    sold = db.Column(db.Integer, default=0)
    manufacture = db.Column(db.Text)
    expiry = db.Column(db.Text)

    def json(self):
        return {'id': self.id, 'category': self.category, 'name': self.name, 'quantity': self.quantity, 'price': self.price, 'description': self.Description}

class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, nullable=False)

    def json(self):
        return {'id': self.id, 'name': self.name, 'total': self.total, 'sold': self.sold}

class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def json(self):
        return {'id': self.user_id, 'name': self.name, 'password': self.password}


class cart(db.Model):
    __table_name__ = 'cart'

    sno = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"))
    quantity = db.Column(db.Integer)

    def json(self):
        return {'sno':self.sno, 'user_id': self.user_id, 'product_id': self.product_id, 'quantity': self.quantity}
