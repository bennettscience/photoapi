from flask_restful import Resource, reqparse, fields, marshal
from app import api
from app.models import Photo


# Return all photos with a consistent URL
photo_fields = {
    "title": fields.String(),
    "upload_date": fields.Integer(),
    "public": fields.Boolean(),
    "uri": fields.Url("photo"),
}


class PhotoListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "title",
            type="str",
            required=True,
            help="no photo title provided",
            location="json",
        )
        super(PhotoListAPI, self).__init__()

    # TODO: Return only public for non-logged in user
    def get(self):
        query = Photo.query.all()
        photos = [marshal(photo, photo_fields) for photo in query]
        return photos


class PhotoAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type="str", location="json")
        self.reqparse.add_argument("description", type="str", location="json")
        self.reqparse.add_argument("public", type=bool, location="json")
        super(PhotoAPI, self).__init__()

    def get(self, id):
        photo = Photo.query.get(id)
        return {"photo": marshal(photo, photo_fields)}

    def post(self):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass


api.add_resource(PhotoListAPI, "/api/v1.0/photos", endpoint="photos")
api.add_resource(PhotoAPI, "/api/v1.0/photos/<id>", endpoint="photo")
