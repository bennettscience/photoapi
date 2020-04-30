import unittest
import json
from app import app, db
from app.models import Photo


class PhotoAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        p = Photo("something", 123456, 0)
        db.session.add(p)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_photo_by_id(self):
        resp = self.client.get("/api/v1.0/photos/1")
        data = resp.json
        self.assertEqual("something", data["photo"]["title"])
        self.assertFalse(data["photo"]["public"])
        self.assertTrue(resp.status_code == 200)

    def test_missing_photo_by_id(self):
        resp = self.client.get("/api/v1.0/photos/4")
        self.assertTrue(resp.status_code == 404)

    def test_photo_upload(self):
        photo = {"title": "test upload 1", "upload_date": 123456, "public": 0}
        headers = {"Content-Type": "application/json"}
        # TODO: This sends JSON, not a form. Convert to form input
        resp = self.client.post(
            "/api/v1.0/photos", data=json.dumps(photo), headers=headers
        )
        self.assertEqual(resp.status_code, 201, "The result should be 201 created")
        self.assertIsInstance(resp.json, dict, "The api should return an object")

    def test_photo_title_update(self):
        photo = {"title": "This is an update"}
        headers = {"Content-Type": "application/json"}
        resp = self.client.put(
            "/api/v1.0/photos/1", data=json.dumps(photo), headers=headers
        )
        data = resp.json
        self.assertEqual(resp.status_code, 200, "The photo was updated")
        self.assertEqual(data["photo"]["title"], "This is an update")
        self.assertEqual(
            data["photo"]["public"], 0, "The public option has not changed"
        )
