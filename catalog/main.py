from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, PerfumeCompanyName, PerfumeName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///perfumes.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Perfumes Cart"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
vrs_cat = session.query(PerfumeCompanyName).all()


# login
@app.route('/login')
def showLogin():

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    vrs_cat = session.query(PerfumeCompanyName).all()
    vres = session.query(PerfumeName).all()
    return render_template('login.html',
                           STATE=state, vrs_cat=vrs_cat, vres=vres)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    NewUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(NewUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# It shows Home


@app.route('/')
@app.route('/home')
def home():
    vrs_cat = session.query(PerfumeCompanyName).all()
    return render_template('myhome.html', vrs_cat=vrs_cat)


# perfumemart=PerfumeMart Category for admins
@app.route('/perfumemart')
def PerfumeMart():
    try:
        if login_session['username']:
            name = login_session['username']
            vrs_cat = session.query(PerfumeCompanyName).all()
            vrs = session.query(PerfumeCompanyName).all()
            vres = session.query(PerfumeName).all()
            return render_template('myhome.html', vrs_cat=vrs_cat,
                                   vrs=vrs, vres=vres, uname=name)
    except:
        return redirect(url_for('showLogin'))


# Showing Perfumes based on Perfume category
@app.route('/perfumemart/<int:vrid>/AllModels')
def showPerfumes(vrid):
    vrs_cat = session.query(PerfumeCompanyName).all()
    vrs = session.query(PerfumeCompanyName).filter_by(id=vrid).one()
    vres = session.query(PerfumeName).filter_by(
        perfumecompanynameid=vrid).all()
    try:
        if login_session['username']:
            return render_template('showPerfumes.html', vrs_cat=vrs_cat,
                                   vrs=vrs, vres=vres,
                                   uname=login_session['username'])
    except:
        return render_template('showPerfumes.html',
                               vrs_cat=vrs_cat, vrs=vrs, vres=vres)


# Adds New Perfume
@app.route('/perfumemart/addPerfumeModel', methods=['POST', 'GET'])
def addPerfumeModel():
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        perfume = PerfumeCompanyName(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(perfume)
        session.commit()
        return redirect(url_for('PerfumeMart'))
    else:
        return render_template('addPerfumeModel.html', vrs_cat=vrs_cat)


# It is For Edit Perfume Category
@app.route('/perfumemart/<int:vrid>/edit', methods=['POST', 'GET'])
def editPerfumeCategory(vrid):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    editedPerfume = session.query(PerfumeCompanyName).filter_by(id=vrid).one()
    creator = getUserInfo(editedPerfume.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Perfume Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('PerfumeMart'))
    if request.method == "POST":
        if request.form['name']:
            editedPerfume.name = request.form['name']
        session.add(editedPerfume)
        session.commit()
        flash("Perfume Category Edited Successfully")
        return redirect(url_for('PerfumeMart'))
    else:
        # vrs_cat is global variable we can them in entire application
        return render_template('editPerfumeCategory.html',
                               vr=editedPerfume, vrs_cat=vrs_cat)


# It is for Delete Perfume Category
@app.route('/perfumemart/<int:vrid>/delete', methods=['POST', 'GET'])
def deletePerfumeCategory(vrid):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    vr = session.query(PerfumeCompanyName).filter_by(id=vrid).one()
    creator = getUserInfo(vr.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Perfume Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('PerfumeMart'))
    if request.method == "POST":
        session.delete(vr)
        session.commit()
        flash("Perfume Category Deleted Successfully")
        return redirect(url_for('PerfumeMart'))
    else:
        return render_template(
            'deletePerfumeCategory.html', vr=vr, vrs_cat=vrs_cat)


# Add New Perfume Details
@app.route('/perfumemart/addModel/addPerfumeDetails/<string:vrname>/add',
           methods=['GET', 'POST'])
def addPerfumeDetails(vrname):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    vrs = session.query(PerfumeCompanyName).filter_by(name=vrname).one()
    # See if the logged in user is not the owner of perfume
    creator = getUserInfo(vrs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Perfume"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showPerfumes', vrid=vrs.id))
    if request.method == 'POST':
        name = request.form['name']
        flavour = request.form['flavour']
        color = request.form['color']
        cost = request.form['cost']
        rlink = request.form['rlink']
        perfumedetails = PerfumeName(
            name=name, flavour=flavour,
            color=color, cost=cost,
            rlink=rlink,
            date=datetime.datetime.now(),
            perfumecompanynameid=vrs.id,
            user_id=login_session['user_id'])
        session.add(perfumedetails)
        session.commit()
        return redirect(url_for('showPerfumes', vrid=vrs.id))
    else:
        return render_template('addPerfumeDetails.html',
                               vrname=vrs.name, vrs_cat=vrs_cat)


# Edit perfume details
@app.route('/perfumemart/<int:vrid>/<string:vrename>/edit',
           methods=['GET', 'POST'])
def editPerfume(vrid, vrename):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    vr = session.query(PerfumeCompanyName).filter_by(id=vrid).one()
    perfumedetails = session.query(PerfumeName).filter_by(name=vrename).one()
    # See if the logged in user is not the owner of perfume
    creator = getUserInfo(vr.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this perfume"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showPerfumes', vrid=vr.id))
    # POST methods
    if request.method == 'POST':
        perfumedetails.name = request.form['name']
        perfumedetails.flavour = request.form['flavour']
        perfumedetails.color = request.form['color']
        perfumedetails.cost = request.form['cost']
        perfumedetails.rlink = request.form['rlink']
        perfumedetails.date = datetime.datetime.now()
        session.add(perfumedetails)
        session.commit()
        flash("Perfume Edited Successfully")
        return redirect(url_for('showPerfumes', vrid=vrid))
    else:
        return render_template('editPerfume.html',
                               vrid=vrid, perfumedetails=perfumedetails,
                               vrs_cat=vrs_cat)


# Delete Perfume Details
@app.route('/perfumemart/<int:vrid>/<string:vrename>/delete',
           methods=['GET', 'POST'])
def deletePerfume(vrid, vrename):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    vr = session.query(PerfumeCompanyName).filter_by(id=vrid).one()
    perfumedetails = session.query(PerfumeName).filter_by(name=vrename).one()
    # See if the logged in user is not the owner of perfume
    creator = getUserInfo(vr.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this perfume"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showPerfumes', vrid=vr.id))
    if request.method == "POST":
        session.delete(perfumedetails)
        session.commit()
        flash("Deleted Perfume Successfully")
        return redirect(url_for('showPerfumes', vrid=vrid))
    else:
        return render_template('deletePerfume.html',
                               vrid=vrid, perfumedetails=perfumedetails,
                               vrs_cat=vrs_cat)


# Logout from user
@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json
# Displays all the details that we have
@app.route('/perfumemart/JSON')
def allPerfumesJSON():
    perfumecategories = session.query(PerfumeCompanyName).all()
    category_dict = [c.serialize for c in perfumecategories]
    for c in range(len(category_dict)):
        perfumes = [i.serialize for i in session.query(
                 PerfumeName).filter_by(
                     perfumecompanynameid=category_dict[c]["id"]).all()]
        if perfumes:
            category_dict[c]["rifle"] = perfumes
    return jsonify(PerfumeCompanyName=category_dict)

# Displays the Perfumes Catagories


@app.route('/perfumemart/perfumeCategories/JSON')
def categoriesJSON():
    rifles = session.query(PerfumeCompanyName).all()
    return jsonify(perfumeCategories=[c.serialize for c in rifles])

# Displays all Rifle Details in Rifle catagories


@app.route('/perfumemart/perfumes/JSON')
def itemsJSON():
    items = session.query(PerfumeName).all()
    return jsonify(perfumes=[i.serialize for i in items])

# Displays details of perfumes in category wise


@app.route('/perfumemart/<path:perfume_name>/perfumes/JSON')
def categoryItemsJSON(perfume_name):
    perfumeCategory = session.query(
        PerfumeCompanyName).filter_by(name=perfume_name).one()
    perfumes = session.query(PerfumeName).filter_by(
        perfumecompanyname=perfumeCategory).all()
    return jsonify(perfumes=[i.serialize for i in perfumes])

# Displays the details of a perticular perfume


@app.route('/perfumemart/<path:perfumemodel_name>/<path:perfume_name>/JSON')
def ItemJSON(perfumemodel_name, perfume_name):
    perfumeCategory = session.query(
        PerfumeCompanyName).filter_by(name=perfumemodel_name).one()
    PerfumeEdition = session.query(PerfumeName).filter_by(
           name=perfume_name, perfumecompanyname=perfumeCategory).one()
    return jsonify(PerfumeEdition=[PerfumeEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8888)
