import unittest
from app import app, db
from app.models import Photo


class AllPhotosTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
        self.client = app.test_client()

        p1 = Photo('something', 123456, 0)
        p2 = Photo('something else', 999123, 1)
        db.session.add_all([p1, p2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # The API returns a list of objects
    def test_get_all_photos(self):
        resp = self.client.get('/api/v1.0/photos')
        self.assertIsInstance(resp.json, list)
        self.assertEqual(2, len(resp.json))
        self.assertTrue(resp.status_code == 200)
