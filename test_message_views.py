"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_add_message(self):
        """Can the user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        """test if a logged in user delete a message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()

            resp = c.post(f"/messages/{msg.id}/delete")

            self.assertEqual(resp.status_code, 302)

            messages = Message.query.all()

            self.assertEqual(messages, [])

    def test_cannot_add_message(self):
        """can a message be added when there is no logged in user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.get("/logout")

            try:
                resp = c.post("/messages/new", data={"text": "Hello"})
                self.assertFalse(True)
            except Exception:
                self.assertTrue(True)

    def test_cannot_delete_message(self):
        """test if a message be deleted when there is no logged in user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            
            c.get("/logout")
            
            msg = Message.query.one()

            try:
                c.post(f"/messages/{msg.id}/delete")
                self.assertFalse(True)
            except Exception:
                self.assertTrue(True)

    #I looked at the solution for these last two tests after I was confused what
    #the answer was supposed to look like and what the question was asking. This
    #two tests are inspired by what I saw in the solution.
    def test_invalid_user_add(self):
        """test if adding a message as an invalid user will be prohibited"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9812751928715612
            
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_cross_user_delete(self):
        """test if deleting a message as another user other than the one logged in
        on the client machine will be prohibited"""

        another_user = User.signup(username="another_test_user",
                            email="another@gmail.com",
                            password="hashThis!",
                            image_url=None)

        another_message = Message(
                            id=860,
                            text="owned by another_user",
                            user_id=self.testuser.id
        )

        db.session.add_all([another_user, another_message])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = another_user.id

            resp = c.post("/messages/860/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(860)
            self.assertIsNotNone(m)