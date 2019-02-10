from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Search

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_searches(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four searches
        now = datetime.utcnow()
        s1 = Search(playlist="https://itunes.apple.com/il/playlist/nov18/pl.u-XkD04Mpf2pjzq5", author=u1,
                  timestamp=now + timedelta(seconds=1))
        s2 = Search(playlist="https://itunes.apple.com/il/playlist/dec18/pl.u-06oxDvbuYvDVbK", author=u2,
                  timestamp=now + timedelta(seconds=4))
        s3 = Search(playlist="https://itunes.apple.com/us/playlist/post-malone-essentials/pl.8c2c23f9775a4e6a99a4d123ceb192a8", author=u3,
                  timestamp=now + timedelta(seconds=3))
        s4 = Search(playlist="https://itunes.apple.com/us/playlist/swaecation/pl.u-2x1zuL15l07", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed searches of each user
        f1 = u1.followed_searches().all()
        f2 = u2.followed_searches().all()
        f3 = u3.followed_searches().all()
        f4 = u4.followed_searches().all()
        self.assertEqual(f1, [s2, s4, s1])
        self.assertEqual(f2, [s2, s3])
        self.assertEqual(f3, [s3, s4])
        self.assertEqual(f4, [s4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
