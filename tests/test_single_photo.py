import os
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

        upload = Photo("Existing Photo", 123456, 0, 'hello.jpg')
        db.session.add(upload)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_photo_by_id(self):
        resp = self.client.get("/api/v1.0/photos/1")
        photo = resp.json
        self.assertEqual("Existing Photo", photo["title"])
        self.assertFalse(photo["public"])
        self.assertTrue(resp.status_code == 200)

    def test_missing_photo_by_id(self):
        resp = self.client.get("/api/v1.0/photos/4")
        self.assertTrue(resp.status_code == 404)

    def test_photo_upload(self):
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

        photo = resp.json

        self.assertEqual(resp.status_code, 201, "The result should be 201 created")
        self.assertIsInstance(resp.json, dict, "The api should return an object")
        self.assertEqual(photo['filename'], 'hello.jpg')
        self.assertFalse(photo['public'])

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
        photo = resp.json
        self.assertEqual(resp.status_code, 200, "The photo was updated")
        self.assertEqual(photo["title"], "This is an update")
        self.assertEqual(
            photo["public"], 0, "The public option has not changed"
        )

    def test_all_update(self):
        update = {
            "title": "Update existing",
            "public": True
        }
        headers = {"Content-Type": "application/json"}
        resp = self.client.put(
            "/api/v1.0/photos/1", data=json.dumps(update), headers=headers
        )
        photo = resp.json
        self.assertEqual("Update existing", photo["title"], )
        self.assertTrue(photo["public"])

    def test_get_and_update_title(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {
            "title": "Update existing"
        }

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["id"]}', data=json.dumps(update), headers=headers
        )

        self.assertTrue(resp.status_code == 200)
        self.assertEqual("Update existing", resp.json["title"])

    def test_get_and_update_public(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {
            "public": not photo["public"]
        }

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["id"]}', data=json.dumps(update), headers=headers
        )

        self.assertTrue(resp.status_code == 200)
        self.assertTrue(resp.json["public"], "The photo was made public")

    def test_get_and_update_all(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {
            "title": "Update existing",
            "public": not photo["public"]
        }

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["id"]}', data=json.dumps(update), headers=headers
        )

        self.assertTrue(resp.json["public"])
        self.assertEqual("Update existing", resp.json["title"])

    def test_bad_update(self):
        photo = self.client.get(
            "/api/v1.0/photos/1"
        ).json

        headers = {"Content-Type": "application/json"}

        update = {}

        resp = self.client.put(
            f'/api/v1.0/photos/{photo["id"]}', data=json.dumps(update), headers=headers
        )

        self.assertEqual(resp.status_code, 400, "There was no data to update")

    def test_delete_photo(self):

        headers = {
            "Content-Type": "application/json"
        }

        resp = self.client.delete(
            f'/api/v1.0/photos/1', headers=headers
        )

        photo = resp.json

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(photo["message"] == "Successfully deleted")

    def test_get_file_name(self):
        headers = {
            "Content-Type": "application/json"
        }

        resp = self.client.get(
            f'/api/v1.0/photos/1', headers=headers
        )

        photo = resp.json
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(photo["filename"], 'hello.jpg')
