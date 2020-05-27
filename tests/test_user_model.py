import unittest
from app import app, db
from app.models import User


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hash(self):
        user = User(username='test')
        user.set_password('demo')
        self.assertFalse(user.check_password('other'))
        self.assertTrue(user.check_password('demo'))
