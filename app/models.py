from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))    
#Because Flask-Login knows nothing about databases,
#it needs the application's help in loading a user.
#this gives login the users id
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#this class implements the users table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    searches = db.relationship('Search', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    def followed_searches(self):
        followed = Search.query.join(
            followers, (followers.c.followed_id == Search.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Search.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Search.timestamp.desc())
        
    def __repr__(self):
        return '<User {}>'.format(self.username)
#this class implements the Searches table
class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spusername = db.Column(db.String(100), index=False, unique=False)
    playlist = db.Column(db.String(120), index=False, unique=False)
    playlistname = db.Column(db.String(120), index=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Search {} by {}>'.format(self.playlistname, self.spusername)
