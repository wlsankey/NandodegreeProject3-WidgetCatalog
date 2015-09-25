# IMPORT flask, ORM, and web request modules (Base infrastucture)
from catalog import app
from flask import Flask, render_template, request, redirect, url_for, flash

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Users, Category, Item, Comments_Item

import httplib2
import json
from flask import make_response
import requests

from datetime import datetime

# IMPORT for JSON API endpoints
from flask import jsonify

# IMPORT oauth 2.0 and session modules (authenication and authorization infastructure)

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


# DATABASE SETUP
# Connect to database and create database session

engine = create_engine('postgresql:///model')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

# AUTHORIZATION/AUTHENTICATION
# Connect and disconnect users via a third-party Oauth 2.0 solutions


CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']


# CONNECT users

@app.route('/gconnect', methods=['GET','POST'])
def gconnect():
    # "Validate state token"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #  Obtain authorization code
    code = request.data

    try:
        print "Upgrade the authorization code into a credentials object"
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # " Check that the access token is valid."
    access_token = credentials.access_token
    print "PRINT ACCESS TOKEN TEST"
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    #  "If there was an error in the access token info, abort."
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # "Verify that the access token is used for the intended user."
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # "Verify that the access token is valid for this app."
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # "Store the access token in the session for later use."
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # "Get user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    #  ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    #  see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


#  User Helper Functions


def createUser(login_session):
    newUser = Users(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None

# Set state code for login session

@app.route('/login')
def showLogin():
	# Create state token to prevent request forgery
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

	# Store state token in the login_session for later validation
	login_session['state'] = state

	# return"The current session state is %s" %login_session['state']
	return render_template("login.html", STATE=state)


# DISCONNECT -- Revoke a current user's token and reset their login_session.

@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnnect a user.
	
	# credentials = login_session.get('credentials')
	credentials = login_session.get('credentials')
	print "TEST TEST TEST"
	print credentials
	print "END END END"
	if credentials is None:
		response = make_response(json.dumps('Current user is not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		print "Credentials is NONE"
		return response
	# Execute HTTP GET request to revoke current token
	access_token = credentials
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %access_token
	print url
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		# Reset the user's session.
		print "RESULT status at 200!!!"
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']

		response = make_response(json.dumps('Successfully disconected.'), 200)
		response.headers['Content-Type']='application/json'
		return redirect(url_for('showHomepage'))
	if result['status'] != '200':
		response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response
	print "Did not return response!!!"




# VIEWS 
# for templates and routing

@app.route('/')
@app.route('/main/')
@app.route('/home/')
def showHomepage():
	categories = session.query(Category).order_by(desc(Category.no_of_visits))[0:10]
	items = session.query(Item).all()
	print login_session

	return render_template('homepage.html', 
		categories= categories, 
		items= items, 
		login_session=login_session)
	
@app.route('/category/<int:category_id>/')
# Add category_id
def showCategory(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	# Add to Number of Visits counter
	if category.no_of_visits is None:
		category.no_of_visits= 1
		session.commit()
	else:
		category.no_of_visits= category.no_of_visits+1
		session.commit()
	category = session.query(Category).filter_by(id=category_id).one()
	category_items = session.query(Item).filter_by(category_id= category_id)
	items_popular =session.query(Item).filter_by(
		category_id=category_id).order_by(
		desc(Item.no_of_visits))[0:8]
	return render_template('category.html', 
		category_items=category_items, 
		category=category, 
		items_popular=items_popular, 
		login_session=login_session)

@app.route('/category/all')
# Show all categories in database
def ShowCategories_all():
	all_categories = session.query(Category).order_by(asc(Category.name))
	return render_template('all_categories.html', 
		all_categories=all_categories, 
		login_session=login_session)


@app.route('/category/new/', methods= ['GET', 'POST'])
def createNewCategory():
	if 'username' not in login_session:
		return redirect('/login')

	if request.method == 'POST':
		newCategory = Category(
			name= request.form['name'], 
			no_of_visits=1, 
			user_id=login_session['user_id'])
		session.add(newCategory)
		flash("New Category %s successfully created" %newCategory.name)
		session.commit()
		return redirect(url_for('showHomepage'))
	else:
		return render_template('newCategory.html', 
			login_session=login_session)


@app.route('/category/<int:category_id>/edit', methods = ['GET', 'POST'])
def editCategory(category_id):
	
	editedCategory = session.query(Category).filter_by(id=category_id).one()

	# Objects needed for none-authorized users
	creator = getUserInfo(editedCategory.user_id)
	category_items = session.query(Item).filter_by(
		category_id= category_id)
	items_popular =session.query(Item).filter_by(
		category_id=category_id).order_by(desc(Item.no_of_visits))[0:8]
	
	if 'username' not in login_session or creator.id !=login_session['user_id']:
		if editedCategory.no_of_visits is None:
			editedCategory.no_of_visits= 1
			session.commit()
		else:
			editedCategory.no_of_visits= editedCategory.no_of_visits+1
			session.commit()
		flash("You must login to edit category.")
		return render_template('category_public.html', 
			category_items=category_items, 
			category=editedCategory, 
			items_popular=items_popular, 
			login_session=login_session)

	if request.method == 'POST':
		if request.form['name']:
			editedCategory.name = request.form['name']
			session.commit()
			flash('Category successfully edited %s!' %editedCategory.name)
			return redirect(url_for('showCategory', 
				category_id= editedCategory.id))
	else:
		return render_template('editedCategory.html', 
			category= editedCategory, 
			login_session=login_session)

	
@app.route('/category/<int:category_id>/delete', methods= ['GET', 'POST'])
def deleteCategory(category_id):
	deletedCategory = session.query(Category).filter_by(id=category_id).one()

	# Objects needed for none authorized users
	creator = getUserInfo(deletedCategory.user_id)
	category_items = session.query(Item).filter_by(
		category_id= category_id)
	items_popular =session.query(Item).filter_by(
		category_id=category_id).order_by(desc(Item.no_of_visits))[0:8]

	if 'username' not in login_session or creator.id !=login_session['user_id']:
		if deletedCategory.no_of_visits is None:
			deletedCategory.no_of_visits= 1
			session.commit()
		else:
			deletedCategory.no_of_visits= deletedCategory.no_of_visits+1
			session.commit()
		flash("You must login to delete category or be the creator of the category.")
		return render_template('category_public.html', 
			category_items=category_items, 
			category=deletedCategory, 
			items_popular=items_popular, 
			login_session=login_session)
	
	try:
		if request.method == 'POST':
			session.delete(deletedCategory)
			session.commit()
			flash("You have deleted %s" %deletedCategory.name)
			return redirect(url_for('showHomepage'))

		else:
			return render_template('deletedCategory.html', 
				category=deletedCategory, 
				login_session=login_session)
	except IntegrityError:
		return "You cannot delete a category that already has items posted to it."
	else:
		return render_template('deletedCategory.html', 
			category=deletedCategory, 
			login_session=login_session)


@app.route('/category/<int:category_id>/item/<int:item_id>')
def showItem(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	if item.no_of_visits is None:
		item.no_of_visits = 1
		session.commit()
	else:
		item.no_of_visits = (item.no_of_visits + 1)
		session.commit()
	item = session.query(Item).filter_by(id=item_id).one()
	category = session.query(Category).filter_by(id=category_id).one()
	comments = session.query(Comments_Item).filter_by(item_id=item_id).all()

	return render_template('item.html', 
		item=item, 
		category=category, 
		comments= comments, 
		login_session=login_session)

@app.route('/category/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	category = session.query(Category).filter_by(id=category_id).one()

	# Objects needed for none authorized users
	creator = getUserInfo(item.user_id)


	if 'username' not in login_session or creator.id !=login_session['user_id']:
		if item.no_of_visits is None:
			item.no_of_visits= 1
			session.commit()
		else:
			item.no_of_visits= item.no_of_visits+1
			session.commit()
		flash("You must login to edit an item or be the creator of the item.")
		return render_template('item_public.html', 
			category=category, 
			item=item, 
			login_session=login_session)

	if request.method =='POST':
		if request.form['name']:
			item.name = request.form['name']
			session.commit()
		if request.form['description']:
			item.description = request.form['description']
			session.commit()
		if request.form['picture_1']:
			item.picture_1 = request.form['picture_1']
			session.commit()
		if request.form['picture_2']:
			item.picture_2 = request.form['picture_2']
			session.commit()
		if request.form['picture_3']:
			item.picture_3 = request.form['picture_3']
			session.commit()
		if request.form['picture_4']:
			item.picture_4 = request.form['picture_4']
			session.commit()
		flash("You have successfully updated %s" %item.name)
		return redirect(url_for('showItem', 
			category_id= category.id, 
			item_id=item.id))
	else:
		return render_template('editItem.html', 
			category=category, 
			item=item, 
			login_session=login_session)


@app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET','POST'])
def deleteItem(category_id, item_id):
	deletedItem = session.query(Item).filter_by(id=item_id).one()
	category = session.query(Category).filter_by(id=category_id).one()

	# Objects needed for none authorized users
	creator = getUserInfo(deletedItem.user_id)


	if 'username' not in login_session or creator.id !=login_session['user_id']:
		if deletedItem.no_of_visits is None:
			deletedItem.no_of_visits= 1
			session.commit()
		else:
			deletedItem.no_of_visits= deletedItem.no_of_visits+1
			session.commit()
		flash("You must login to edit an item or be the creator of the item.")
		return render_template('item_public.html', 
			category=category, 
			item=deletedItem, 
			login_session=login_session)


	if request.method =='POST':
		session.delete(deletedItem)
		session.commit()
		flash("You have successfully deleted %s" %deletedItem.name)
		return redirect(url_for('showCategory',
			category_id=category_id))

	else:
		return render_template('deleteItem.html', 
			category=category, 
			item=deletedItem, 
			login_session=login_session)


@app.route('/category/<int:category_id>/item/new', methods=['GET','POST'])
def newItem(category_id):
	# current_date = datetime()
	if 'username' not in login_session:
		return redirect('/login')
	category = session.query(Category).filter_by(id=category_id).one()
	if request.method =='POST':
		newItem = Item(
			name= request.form['name'], 
			description= request.form['description'], 
			picture_1= request.form['picture_1'], 
			picture_2=request.form['picture_2'], 
			picture_3= request.form['picture_3'], 
			picture_4=request.form['picture_4'], 
			category_id=category_id, 
			user_id=login_session['user_id'])
		session.add(newItem)
		flash("You've succuessfully added %s" %request.form['name'])
		session.commit()
		return redirect(url_for('showCategory', 
			category_id= category_id ))
		# return redirect(url_for('showCategory',category_id=category_id))

	# else:
	# 	return "To add an itme you must include at least a name and a description."

	else:
		return render_template('newItem.html', 
			category=category, 
			login_session=login_session)



#  JSON API ENDPOINTS for VIEWS

@app.route('/category/all/JSON')
# Show all categories in database
def ShowCategories_all_JSON():
	all_categories = session.query(Category).order_by(asc(Category.name))
	return jsonify(all_categories=[i.serialize for i in all_categories])


@app.route('/category/<int:category_id>/JSON')
# Add category_id
def showCategory_JSON(category_id):
	# category = session.query(Category).filter_by(id=category_id).one()
	category_items = session.query(Item).filter_by(category_id= category_id)
	# items_popular =session.query(Item).filter_by(category_id=category_id).order_by(asc(Item.no_of_likes))[0:8]
	return jsonify(items=[i.serialize for i in category_items])

@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def showItem_JSON(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	# category = session.query(Category).filter_by(id=category_id).one()
	# comments = session.query(Comments_Item).filter_by(item_id=item_id).all()
	return jsonify(item=item.serialize)

@app.route('/allitems/JSON')
def allItems_JSON():
	all_items = session.query(Item).order_by(desc(Item.no_of_visits))
	return jsonify(all_items=[i.serialize for i in all_items])
