import unittest
from app import app, db
from app.models import Photo


class PhotoModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

        photo = Photo('something', 123456, 0)
        db.session.add(photo)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_new_photo(self):
        photo = Photo('something else', 999999, 0)
        db.session.add(photo)
        db.session.commit()

        self.assertTrue(photo.title == 'something else')

    def test_get_id(self):
        photo = Photo.query.get(1)
        self.assertEqual(1, photo.get_id())

    def test_set_public(self):
        photo = Photo.query.get(1)
        photo.set_public()
        self.assertTrue(photo.public)

    def test_set_title(self):
        photo = Photo.query.get(1)
        photo.set_title('A different title')
        self.assertEqual('A different title', photo.title)
        self.assertNotEqual('something else', photo.title)
