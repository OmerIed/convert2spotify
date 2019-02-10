from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import SearchForm, LoginForm
from flask_login import current_user, login_user
from app.models import User, Search
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.convert import Convert
import os, urllib, base64, json
import requests
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        os.environ['PLAYLIST_URL'] = form.playlist.data
        os.environ['SPOTIFY_USERNAME'] = form.spusername.data
        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": 'user-library-read playlist-modify-private playlist-modify-public',
            "client_id": os.environ.get('SPOTIPY_CLIENT_ID')
            }
        url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
        auth_url = "{}/?{}".format("https://accounts.spotify.com/authorize", url_args)
        print('redirecting..')
        return redirect(auth_url)
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        searches = current_user.followed_searches().paginate(
            page, app.config['SEARCHES_PER_PAGE'], False)
        next_url = url_for('index', page=searches.next_num) \
            if searches.has_next else None
        prev_url = url_for('index', page=searches.prev_num) \
            if searches.has_prev else None
        return render_template('index.html', title='Home', form=form,
                               searches=searches.items, next_url=next_url,
                               prev_url=prev_url)
    else:
        return render_template('index.html', title='Home', form=form)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    searches = user.searches.order_by(Search.timestamp.desc()).paginate(
        page, app.config['SEARCHES_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=searches.next_num) \
        if searches.has_next else None
    prev_url = url_for('user', username=user.username, page=searches.prev_num) \
        if searches.has_prev else None
    return render_template('user.html', user=user, searches=searches.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/callback/q')
def callback():
    print('getting code')
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
        }
    base64encoded = base64.urlsafe_b64encode("{}:{}".format(os.environ.get('SPOTIPY_CLIENT_ID'), os.environ.get('SPOTIPY_CLIENT_SECRET')).encode()).decode()
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post("https://accounts.spotify.com/api/token", data=code_payload, headers=headers)
    response_data = json.loads(post_request.text)
    print(response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    print("starting conversion")
    Convert.after_token(access_token)
    return redirect(url_for('index'))
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    searches = Search.query.order_by(Search.timestamp.desc()).paginate(
        page, app.config['SEARCHES_PER_PAGE'], False)
    next_url = url_for('explore', page=searches.next_num) \
        if searches.has_next else None
    prev_url = url_for('explore', page=searches.prev_num) \
        if searches.has_prev else None
    return render_template("index.html", title='Explore', searches=searches.items,
                           next_url=next_url, prev_url=prev_url)


