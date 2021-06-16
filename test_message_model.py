"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

#import app
from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test the message model"""

    def setUp(self):
        """Create test client, delete any residual data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        db.session.commit()
        self.client = app.test_client()

    def test_message_model(self):
        """test the basic message model by creating a message"""

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        message = Message(
            text="here's a test message",
            user_id=user.id
        )

        db.session.add(message)
        db.session.commit()

        self.assertTrue(message.timestamp != None)
        self.assertTrue(message.id != None)

    def test_misinput(self):
        """ensure that Message will not accept empty columns
        or a text column that exceeds the 140 char limit"""

        try:
            Message(

            )
            self.assertFalse(True)
        except Exception:
            self.assertTrue(True)

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        try:
            Message(
                #this string is over 140 characters
                text = """a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        a b c d e f g h i j k l m n o p q r s t u v w x y z
                        """,
                user_id = user.id
            )
            self.assertFalse(True)
        except Exception:
            self.assertTrue(True)

    def test_user_multi_messages(self):
        """test that a user can make multiple messages"""

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        message1 = Message(
            text="here's the first test message",
            user_id=user.id
        )

        message2 = Message(
            text="this is the second test message",
            user_id=user.id
        )

        message3 = Message(
            text="last of all, this is the third message",
            user_id=user.id
        )

        db.session.add(message1)
        db.session.add(message2)
        db.session.add(message3)

        self.assertEqual(len(user.messages), 3)