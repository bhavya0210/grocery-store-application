from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import current_app as app
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from applications.models import Product, Categories
from applications.database import Base, db, engine
from applications.config import LocalDevelopmentConfig


user_name = "123"
password = '123'

def rendermandash():
#gets all necessary information to be displayed on the manager's dashboard
#returns: #1)number of categpries
        #2)list of categpries
        #3)2-d array of all products where each row has the products of one category

    #get all categories in the invenory
    products = Categories.query.all()

    #create a 2d list for all products belonging to each category in the 
    #inventory to have a neat and organised display, else categories will 
    #be jumbled and difficult to look for products
    #prodmat: product matrix
    prodmat = []

    for cat in products:

        if cat.total == 0:
            catname = cat.name
            #no products for this category yet, prompts to add products
            allofcat = ['empty', catname, 'no products added']

        else:
            #allofcat: all products of that category
            #each list is part of a single row for respective categories
            #list has 3 attributes:category name, quanity and price; all to be displayed
            allofcat = []
            temp = Product.query.filter_by(category=cat.name).all()
            for prod in temp:
                temp2 = [prod.category, prod.name, prod.quantity, prod.price, prod.product_id, prod.manufacture, prod.expiry]
                allofcat.append(temp2)

        #update row of categpry to 2d array        
        prodmat.append(allofcat)

    return (len(products), products, prodmat)


@app.route('/', methods=['GET','POST'])
def welcome():

    if(request.method == 'GET'):
        return render_template('welcome.html')
    
    elif(request.method== 'POST'):
        try:
            if(request.form["inp"] == "admin"):
                return redirect('/admin')
            else:
                return redirect('/customer')       
        except:
            return redirect('/')

#admin login
@app.route('/admin', methods=['GET','POST'])
def admin():

    if request.method == 'GET':
        return render_template('login.html', home=True, admin=True)
    
    else:

        #initial login, check for username and password and accordingly display all
        #categories and products on admin's dashboard by redirecting to 'changes'

        username = request.form["username"]

        if(request.form['password'] != password or username != user_name):
            #wrong username and/or password
            return render_template('login.html', home=False, admin=True)
            
        elif(request.form['password'] == password and username == user_name):
            return redirect('/admin/changes')

        return render_template('mandash.html', empty=True)

#admin's dashboard     
@app.route('/admin/changes', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        l, products, prodmat = rendermandash()

        #if no categpries, show prompt to add one
        if(l == 0):
            return render_template('mandash.html', username=user_name, empty=True)
        
        #render html page to display categpries and their respective products
        elif(l >= 1):
            return render_template('mandash.html', username=user_name, empty=False, categories=products, items=prodmat)


#all below functions redirect to the dashboard after making successful changes to the inventory

#edit/update a product
@app.route('/admin/update/<int:product_id>', methods=['GET','POST'])
def update(product_id):

    #get the details of the product to be edited
    prod = Product.query.filter_by(product_id=product_id).one()
    
    if request.method == 'GET':
        return render_template('new.html', type='update', username=user_name, prod=prod)
    
    else:
        #assign new values as retrieved from the form shown to admin and commit the changes to the db
        prod.name, prod.quantity, prod.price, prod.description, prod.manufacture, prod.expiry = request.form.get("name"), request.form.get("quantity"), request.form.get("price"), request.form.get("description"), request.form.get("manufacture"), request.form.get("expiry")
        db.session.commit()

        return redirect('/admin/changes')
    
#delete a product
@app.route('/admin/delete/<int:product_id>')
def delete(product_id):
    #get the product row and its category
    prod = Product.query.filter_by(product_id=product_id).one()
    cat = Categories.query.filter_by(name=prod.category).one()

    #delete the product record
    db.session.delete(Product.query.filter_by(product_id=product_id).one())
    #decrement total number of products in the category, then commit
    cat.total = int(cat.total)-1

    db.session.commit()
    
    return redirect('/admin/changes')

#add new product to a category
@app.route('/admin/addtocat/<string:category>', methods=['GET','POST'])
def addtocat(category):
    if request.method == 'GET':
        return render_template('new.html', type='tocat', username=user_name, cat=category)
    
    else:
        #get details from admin through form
        name = request.form.get("name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        manufacture = request.form.get("manufacture")
        expiry = request.form.get("expiry")

        #create an object for the new product and add to table
        prod = Product(category=category, name=name, price=price, quantity=quantity, manufacture=manufacture, expiry=expiry)
        db.session.add(prod)
        db.session.commit()

        #update the categories table that a new product has been added, then commit all changes 
        cat = Categories.query.filter_by(name=category).one()
        cat.total = int(cat.total)+1

        db.session.commit()
        
        return redirect('/admin/changes')
    
@app.route('/admin/create-category', methods=['GET', 'POST'])
def addcat():
    if request.method == 'GET':
        return render_template('new.html', type='addcat', username=user_name)

    else:

        catname = request.form.get("catname")
        cat = Categories(name=catname, total=0, sold=0)
        print(catname)

        #add the new record then redirect back to dashboard
        db.session.add(cat)
        db.session.commit()

        return redirect('/admin/changes')
    
@app.route('/admin/search', methods=['GET','POST'])
def adminsearch():
    if request.method == 'POST':
        name = '123'

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
        
        print("item")
        for i in item:
            itemlist.append(i)
            print(i.name)

        print("cat")
        for i in cat:
            itemlist.append(i)
            print(i.name)

        print("price")
        for i in pricesearch:
            itemlist.append(i)
            print(i.name)

        """print("less")
        for i in pricesearchless:
            itemlist.append(i)
            print(i.name)"""

        print("date")
        for i in date:
            itemlist.append(i)
            print(i.name)

        return render_template('mandash.html', empty=False, search=True, user=name, items=itemlist, username='123')
    
@app.route("/admin/deletecat/<string:catname>", methods=['GET', 'POST'])
def deletecat(catname):
    if request.method == 'GET':
        prod = Product.query.filter_by(category=catname).all()

        db.session.delete(Categories.query.filter_by(name=catname).one())
        
        
        for i in prod:
            db.session.delete(i)
            db.session.commit()

        db.session.commit()
        
    return redirect('/admin/changes')

@app.route("/admin/updatecat/<string:catname>", methods=['GET', 'POST'])
def updatecat(catname):
    cat = Categories.query.filter_by(name=catname).one()
    if request.method == 'GET':
                
        return render_template('new.html', type='updatecat', username=user_name, details=cat)
    
    else:
        name = request.form["name"]

        cat.name = name

        prodlist = Product.query.filter_by(category=catname).all()
        for prod in prodlist:
            prod.category = name
            
        db.session.commit()

        return redirect('/admin/changes')

@app.route('/admin/summary')
def summary():
    total = []
    sold = []
    name = []

    data = Categories.query.all()

    for item in data:
        total.append(item.total)
        sold.append(item.sold)
        name.append(item.name)

    print(total)
    print(sold)
    print(name)

    fig, ax = plt.subplots()
    fig.set_facecolor('maroon')
    ax.set_facecolor('maroon')
    ax.bar(name,total,color="yellow")
    plt.ylabel('items in each category',color='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white')
    plt.savefig('./code/static/total.png')

    maxtot = name[total.index(max(total))]
    maxsold = name[sold.index(max(sold))]

    fig, ax = plt.subplots()
    fig.set_facecolor('maroon')
    ax.set_facecolor('maroon')
    ax.bar(name,sold,color="yellow")
    plt.ylabel('number of sells in each category',color='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white')
    plt.savefig('./code/static/sold.png')


    return render_template('summary.html', maxtot=maxtot, maxsold=maxsold)