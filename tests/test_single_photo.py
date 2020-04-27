import unittest
from app import app, db
from app.models import Photo


class PhotoAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
        self.client = app.test_client()

        p = Photo('something', 123456, 0)
        db.session.add(p)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_photo_by_id(self):
        resp = self.client.get('/photos/api/v1.0/photos/1')
        data = resp.json
        self.assertEqual('something', data['photo']['title'])
        self.assertFalse(data['photo']['public'])
