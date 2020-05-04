import unittest
import json
from io import BytesIO
from datetime import datetime
from pathlib import Path
from app import app, db
from app.models import Photo


class PhotoAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        upload = Photo("Existing Photo", 123456, 0, 'uploads/hello.jpg')
        db.session.add(upload)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_photo_by_id(self):
        resp = self.client.get("/api/v1.0/photos/1")
        data = resp.json
        self.assertEqual("Existing Photo", data["photo"]["title"])
        self.assertFalse(data["photo"]["public"])
        self.assertTrue(resp.status_code == 200)

    def test_missing_photo_by_id(self):
        resp = self.client.get("/api/v1.0/photos/4")
        self.assertTrue(resp.status_code == 404)

    def test_photo_upload(self):
        # TODO: This sends JSON, not a form. Convert to form input
        payload = {
            "file": (BytesIO(b'Hello there'), 'hello.jpg'),
            "title": "New file",
            "upload_date": datetime.timestamp(datetime.now()),
            "public": False
        }
        resp = self.client.post(
            "/api/v1.0/photos", buffered=True,
            content_type="multipart/form-data",
            data=payload
        )
        self.assertEqual(resp.status_code, 201, "The result should be 201 created")
        self.assertIsInstance(resp.json, dict, "The api should return an object")

    def test_bad_file_upload(self):
        resp = self.client.post(
            "api/v1.0/photos", buffered=True,
            content_type="multipart/form-data",
            data={"file_field": (BytesIO(b'hello there'), 'hello.txt')}
        )
        self.assertTrue(resp.status_code == 400)

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

    def test_all_update(self):
        update = {
            "title": "Update existing",
            "public": 1
        }
        headers = {"Content-Type": "application/json"}
        resp = self.client.put(
            "/api/v1.0/photos/1", data=json.dumps(update), headers=headers
        )
        data = resp.json
        self.assertEqual("Update existing", data["photo"]["title"], )
        self.assertTrue(data["photo"]["public"])

    def test_get_and_update_title(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {
            "title": "Update existing"
        }

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["photo"]["id"]}', data=json.dumps(update), headers=headers
        )
        data = resp.json
        self.assertTrue(resp.status_code == 200)
        self.assertEqual("Update existing", data["photo"]["title"])

    def test_get_and_update_public(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {
            "public": not photo["photo"]["public"]
        }

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["photo"]["id"]}', data=json.dumps(update), headers=headers
        )
        data = resp.json
        self.assertTrue(resp.status_code == 200)
        self.assertTrue(data["photo"]["public"], "The photo was made public")

    def test_get_and_update_all(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {
            "title": "Update existing",
            "public": not photo["photo"]["public"]
        }

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["photo"]["id"]}', data=json.dumps(update), headers=headers
        )
        data = resp.json
        self.assertTrue(data["photo"]["public"])
        self.assertEqual("Update existing", data["photo"]["title"])

    def test_bad_update(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {}

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["photo"]["id"]}', data=json.dumps(update), headers=headers
        )
        data = resp.json
        self.assertEqual(resp.status_code, 400, "There was no data to update")

    def test_delete_photo(self):
        headers = {
            "Content-Type": "application/json"
        }

        resp = self.client.delete(
            f'/api/v1.0/photos/1', headers=headers
        )

        data = resp.json
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["message"] == "Successfully deleted")

    def test_get_file_path(self):
        headers = {
            "Content-Type": "application/json"
        }

        resp = self.client.get(
            f'/api/v1.0/photos/1', headers=headers
        )

        data = resp.json
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["photo"]["file_path"], 'uploads/hello.jpg')
