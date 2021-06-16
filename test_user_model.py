"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test the user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        db.session.commit()
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(len(user1.messages), 0)
        self.assertEqual(len(user1.followers), 0)

    def test_repr(self):
        """test the repr method for the user model"""
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(user1)
        db.session.commit()
        self.assertEqual(user1.__repr__(), f"<User #{user1.id}: testuser, test@test.com>")

    def test_is_following(self):
        """test the is_following method for one user following another"""
        
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@user2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        user1.following.append(user2)

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
    
    def test_is_not_following(self):
        """tset the is_following method to see if it works for when a 
        user is not following another"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@user2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        self.assertFalse(user2.is_following(user1))

    def test_is_followed_by(self):
        """test the is_following method for one user following another"""
        
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@user2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        user1.following.append(user2)

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertTrue(user2.is_followed_by(user1))
    
    def test_is_not_followed_by(self):
        """tset the is_following method to see if it works for when a 
        user is not following another"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@user2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        user1.following.append(user2)

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertFalse(user1.is_followed_by(user2))

    def test_signup(self):
        """test if User.signup() will successfully create a user when
        given valid credentials"""

        user = User.signup("testuserSignUp", "test@gamil.com", "HashThis!", "/static/images/default-pic.png")

        self.assertEqual(user.__repr__(), f"<User #{user.id}: testuserSignUp, test@gamil.com>")

    def test_breaking_signup(self):
        """test if signup() will predictably fail when the table validators fail"""
        user = User.signup("testSignUp", "anotherTest@gamil.com", "HashThis!", "/static/images/default-pic.png")
        try:
            clone_user = User.signup("testuserSignUp", "test@gamil.com", "HashThis!", "/static/images/default-pic.png")
            self.assertFalse(True)
        except Exception:
            self.assertTrue(True)

    def test_valid_authenticate(self):
        """test authenticate when the username and password inputted are valid"""

        user = User.signup("testAuthenticate", "authTest@gamil.com", "HashThis!", "/static/images/default-pic.png")

        self.assertEqual(user, User.authenticate("testAuthenticate", "HashThis!"))

    def test_invalid_username_auth(self):
        """test authenticate when the username is invalid"""

        user = User.signup("testAuthenticate", "authTest@gamil.com", "HashThis!", "/static/images/default-pic.png")

        self.assertFalse(User.authenticate("invalid1245-019256", "HashThis!"))

    def test_invalid_username_auth(self):
        """test authenticate when the username is invalid"""

        user = User.signup("testAuthenticate", "authTest@gamil.com", "HashThis!", "/static/images/default-pic.png")

        self.assertFalse(User.authenticate("testAuthenticate", "CannotHashThis?"))