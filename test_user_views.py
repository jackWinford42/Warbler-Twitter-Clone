"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# import app
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_follow_pages(self):
        """test the login route for a user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        user = User.query.one()
        resp = c.get(f"/users/{user.id}/following")
        self.assertEqual(resp.status_code, 200)

        another_user = User.signup(username="another_test_user",
                                    email="another@gmail.com",
                                    password="hashThis!",
                                    image_url=None)

        db.session.commit()

        resp_two = c.get(f"/users/{another_user.id}/following")
        self.assertEqual(resp_two.status_code, 200)

        resp_three = c.get(f"/users/{user.id}/followers")
        self.assertEqual(resp_three.status_code, 200)

        resp_four = c.get(f"/users/{another_user.id}/followers")
        self.assertEqual(resp_four.status_code, 200)

    def test_disallow_follow_pages(self):
        """test if when a user is logged out if they can view the following
        and followers pages for users"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.get("/logout")

            first_user = User.query.filter_by(username="testuser").first()

            resp = c.get(f"/users/{first_user.id}/following")
            self.assertEqual(resp.status_code, 302)

            resp_two = c.get(f"/users/{first_user.id}/followers")
            self.assertEqual(resp_two.status_code, 302)
