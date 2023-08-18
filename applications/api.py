from flask_restful import Resource,Api
from flask_restful import fields, marshal_with,reqparse
from applications.database import db
from applications.models import Product, Users, Categories
import applications.validation as av # import NotFoundError,BusinnessValidationError

output_fields={
    "user_id":fields.Integer,
    "name":fields.String,
}

create_user_parser=reqparse.RequestParser()
create_user_parser.add_argument('user_id',type)
create_user_parser.add_argument('name')

product_fields={
    "product_id":fields.Integer,
    "name": fields.String,
    "quantity": fields.Integer,
    "category": fields.String,
}

create_product_parser=reqparse.RequestParser()
create_product_parser.add_argument('product_id',type)
create_product_parser.add_argument('name')
create_product_parser.add_argument('quantity')
create_product_parser.add_argument('category')


category_fields={
    "id":fields.Integer,
    "name":fields.String,
    "sold":fields.Integer,
    "total":fields.Integer,
}

create_category_parser=reqparse.RequestParser()
create_category_parser.add_argument('id',type)
create_category_parser.add_argument('name')
create_category_parser.add_argument('sold')
create_category_parser.add_argument('total')

class UserAPI(Resource):
    @marshal_with(output_fields)
    def get(self, user_id):
        print("in userapi get method", user_id)
        user = Users.query.filter_by(user_id=user_id).first()
        if user:
            return user
        else:
            raise av.NotFoundError(status_code=404)

    def post(self):
        args = create_user_parser.parse_args()
        username=args.get("username",None)
        password=args.get("password",None)
        if username is None:
            raise av.BusinnessValidationError(status_code=400,error_code="BE1001",error_message="username is required")
        
        user=Users.query.filter_by(name=username).first()
        if user:
            raise av.BusinnessValidationError(status_code=400,error_code="BE1003",error_message="Duplicate")
        
        new_user=Users(name=username,password=password)
        db.session.add(new_user)
        db.session.commit()
        return "",201
    
class ProductApi(Resource):
    @marshal_with(product_fields)
    def get(self,product_id):
        print("in productapi get method", product_id)
        product=Product.query.filter_by(product_id=product_id).first()
        if product:
            return product
        else:
            raise av.NotFoundError(status_code=404)
    @marshal_with(product_fields)
    def put(self, product_id):
        product = Product.query.filter_by(product_id=product_id).first()
        if product is None:
            raise av.NotFoundError(status_code=404)
        args = create_product_parser.parse_args()
        name = args.get("name", None)
        quantity=args.get("quantity")
        category=args.get("category")
        if name is None:
            raise av.NotFoundError(status_code=400)
        else:
            product.name = name
            product.quantity = quantity
            product.category = category
            db.session.add(product)
            db.session.commit()
            return product

    def post(self):
        args=create_user_parser.parse_args()
        name=args.get("name",None)
        quantity=args.get("quantity")
        category=args.get("capcacity")
        if name is None:
            raise av.BusinnessValidationError(status_code=400,error_code="BE1002",error_message="name is required")
        newprod=Product(name=name,quantity=quantity,category=category)
        db.session.add(newprod)
        db.session.commit()
        return "",201
    

class CategoryApi(Resource):
    @marshal_with(category_fields)
    def get(self,id):
        # print("in userapi get method", username)
        cat=Categories.query.filter(Categories.id==id).first()
        if cat:
            return cat
        else:
            raise av.NotFoundError(status_code=404)
    @marshal_with(category_fields)
    def put(self, id):
        cat = Categories.query.filter(Categories.id == id).first()
        if cat is None:
            raise av.NotFoundError(status_code=404)
        args = create_category_parser.parse_args()
        name = args.get("name", None)
        sold = 0
        total = 0
        
        if name is None:
            raise av.NotFoundError(status_code=400)
        else:
            cat.name = name
            cat.sold = sold
            cat.total = total
            db.session.add(cat)
            db.session.commit()
            return cat

    def post(self):
        args=create_user_parser.parse_args()
        name=args.get("name",None)
        sold = 0 
        total = 0

        if name is None:
            raise av.BusinnessValidationError(status_code=400,error_code="BE1002",error_message="name is required")
        new_cat=Categories(name=name,sold=sold, total = total)
        db.session.add(new_cat)
        db.session.commit()
        return "",201