from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import current_app as app
from sqlalchemy import delete

from applications.models import Users, cart, Product, Categories
from applications.database import Base, db, engine
from applications.config import LocalDevelopmentConfig

def rendercustdash(name):
#gets all necessary information to be displayed on the manager's dashboard
#returns: #1)number of categpries
        #2)list of categpries
        #3)2-d array of all products where each row has the products of one category

    #get all categories in the invenory
    products = Categories.query.all()

    #get user id
    user = Users.query.filter_by(name=name).one()
    id = user.user_id

    #create a 2d list for all products belonging to each category in the 
    #inventory to have a neat and organised display, else categories will 
    #be jumbled and difficult to look for products
    #prodmat: product matrix
    prodmat = []

    for cat in products:

        if cat.total == 0:
            catname = cat.name
            #no products for this category yet
            allofcat = ['empty', catname, 'no products added']

        else:
            #allofcat: all products of that category
            #each list is part of a single row for respective categories
            #list has 3 attributes:category name, product name, quanity, price, product id, in cart
            #all but product id to be displayed
            allofcat = []
            temp = Product.query.filter_by(category=cat.name).all()
            for prod in temp:
                #get how many (possibly 0) counts in user's cart at the moment
                item = cart.query.filter_by(user_id=id, product_id=prod.product_id).count()
                
                if(item == 0):
                    #none
                    temp2 = [prod.category, prod.name, prod.quantity, prod.price, prod.product_id, 0, prod.manufacture, prod.expiry]
                    allofcat.append(temp2)
                
                else:
                    #indicate accordingly
                    item = cart.query.filter_by(user_id=id, product_id=prod.product_id).one()
                    if(item.quantity > prod.quantity):
                        item.quantity = prod.quantity
                        db.session.commit()
                    temp2 = [prod.category, prod.name, prod.quantity, prod.price, prod.product_id, item.quantity, prod.manufacture, prod.expiry]
                    allofcat.append(temp2)

        #update row of category to 2d array        
        prodmat.append(allofcat)


    return (len(products), products, prodmat)

@app.route('/customer', methods=['GET','POST'])
def customer():
    if request.method == 'GET':
        print("get")
        return render_template('login.html', home=True, admin=False, mode="login")

    else:

        username = request.form["username"]
        user = Users.query.filter_by(name=username).count()

        if(user==0):
            print("no user")
            return render_template('login.html', home=True, admin=False, mode="add")
        
        else:
            user = Users.query.filter_by(name=username).one()
            if user.password == request.form["password"]:
                return redirect(url_for('dash', name=username))
            else:
                return render_template('login.html', home=False, admin=False, mode="login")
            
@app.route('/customer/dashboard/<name>', methods=['GET', 'POST'])
def dash(name):
    user = Users.query.filter_by(name=name).one()
    l, products, prodmat = rendercustdash(name)

    #if empty, show message that no items in store
    if(l == 0):
        return render_template('custdash.html', empty=True, search=False)
    
    #render html page to display categpries and their respective products
    else:
        return render_template('custdash.html', empty=False, search=False, categories=products, items=prodmat, user=user)


@app.route('/customer/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('createuser.html')
    
    else:
        username, password = request.form.get("name"), request.form.get("password")
        user = Users(name=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/customer')
    
@app.route('/customer/<int:id>/add/<int:prod>/tocart', methods=['GET', 'POST'])
def addtocart(id, prod):
    if request.method == 'GET' or request.method == 'POST':
        quantity = cart.query.filter_by(product_id=prod, user_id=id).count()

        if(quantity == 0):
            item = cart(user_id=id, product_id=prod, quantity=1)
            db.session.add(item)
            db.session.commit()
        else:
            item = cart.query.filter_by(user_id=id, product_id=prod).one()
            if(item.quantity+1 <= Product.query.filter_by(product_id=prod).one().quantity):
                item.quantity += 1
                db.session.commit()

        user = Users.query.filter_by(user_id=id).one()
        name = user.name

        return redirect(url_for('dash', name=name))


@app.route('/customer/<int:id>/cart', methods=['GET', 'POST'])
def customercart(id):
    if request.method == 'GET':
        user = Users.query.filter_by(user_id=id).one().name
        items = cart.query.filter_by(user_id=id).all()

        #itemlist = [item name, quantity in cart, total price, product_id]
        itemlist = []

        total = 0

        for i in items:
            product = Product.query.filter_by(product_id=i.product_id).one()
            priceone = product.price
            name = Product.query.filter_by(product_id=i.product_id).one().name
            carti = cart.query.filter_by(product_id=i.product_id, user_id=id).one()
            quantity = carti.quantity
            print(quantity)
            print(product.quantity)
            if(quantity > product.quantity):
                print("here")
                quantity = product.quantity
                carti.quantity = product.quantity
                db.session.commit()
            priceall = priceone*quantity
        
            item = [name, quantity, priceall, i.product_id]
            itemlist.append(item)
            
            total += priceall

        return render_template('cart.html', name=user, id=id, amt=total, items=itemlist, empty=False)
    else:
        username = Users.query.filter_by(user_id=id).one().name

        items = cart.query.filter_by(user_id=id).all()
        for item in items:
            pid = item.product_id
            prod = Product.query.filter_by(product_id=pid).one()
            prod.quantity -= item.quantity
            prod.sold += item.quantity
            cat = prod.category
            editcat = Categories.query.filter_by(name=cat).one()
            editcat.sold += item.quantity

            others = cart.query.filter_by(product_id=pid).all()
            for one in others:
                if(one.quantity > 0):
                    if(one.quantity - item.quantity < 0):
                        one.quantity = 0
                    else:
                        one.quantity -= item.quantity

            db.session.delete(item)

            db.session.commit()
        
        db.session.commit()

        return render_template('cart.html', name=username, id=id, empty=True)


@app.route('/customer/<int:id>/add/<int:prod>/incart')
def addincart(id, prod):
    item = cart.query.filter_by(user_id=id, product_id=prod).one()
    if(item.quantity+1 <= Product.query.filter_by(product_id=prod).one().quantity):
        item.quantity += 1
        db.session.commit()
    return redirect(url_for('customercart', id=id))

@app.route('/customer/<int:id>/sub/<int:prod>/incart')
def subincart(id, prod):
    item = cart.query.filter_by(user_id=id, product_id=prod).one()
    if(item.quantity-1 >= 0):
        item.quantity -= 1
        db.session.commit()
    return redirect(url_for('customercart', id=id))

@app.route('/customer/<int:id>/del/<int:prod>/incart')
def delincart(id, prod):
    db.session.delete(cart.query.filter_by(user_id=id, product_id=prod).one())
    db.session.commit()
    return redirect(url_for('customercart', id=id))

@app.route('/customer/<int:id>/search', methods=['GET','POST'])
def search(id):
    if request.method == 'POST':
        name = Users.query.filter_by(user_id=id).one()

        keyword = request.form["search"]

        #search for both items and categories for name
        item = Product.query.filter_by(name=keyword).all()
        cat = Product.query.filter_by(category=keyword).all()

        #search for price: first equal to price,
        #then all items less than that price
        pricesearch = Product.query.filter_by(price=keyword).all()
        #pricesearchless = Product.query.filter(Product.price < keyword).all()

        #search for manufacturing date
        date = Product.query.filter_by(manufacture = keyword).all()

        itemlist = []
        
        for i in item:
            itemlist.append(i)

        for i in cat:
            itemlist.append(i)

        for i in pricesearch:
            itemlist.append(i)

        """for i in pricesearchless:
            itemlist.append(i)"""

        for i in date:
            itemlist.append(i)

        return render_template('custdash.html', empty=False, search=True, user=name, items=itemlist)