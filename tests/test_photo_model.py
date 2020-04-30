import unittest
from app import app, db
from app.models import Photo


class PhotoModelCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()

        photo = Photo("Photo1", 123456, 0)
        db.session.add(photo)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_new_photo(self):
        photo = Photo("Photo2", 999999, 0)
        db.session.add(photo)
        db.session.commit()

        self.assertTrue(photo.title == "Photo2")

    def test_get_id(self):
        photo = Photo.query.get(1)
        self.assertEqual(1, photo.get_id())

    def test_set_public(self):
        photo = Photo.query.get(1)
        photo.set_public()
        self.assertTrue(photo.public)

    def test_set_title(self):
        photo = Photo.query.get(1)
        photo.set_title("Photo1 new title")
        self.assertEqual("Photo1 new title", photo.title)
        self.assertNotEqual("Photo1", photo.title)

    def test_title_update(self):
        photo = Photo.query.get(1)
        photo.update("title", "Photo1A")
        self.assertEqual(photo.title, "Photo1A")
        self.assertEqual(photo.public, 0)

    def test_public_update(self):
        photo = Photo.query.get(1)
        photo.update("public", not photo.public)
        self.assertTrue(photo.public)
