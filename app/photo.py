from flask import make_response, jsonify, abort, request, Response
from flask_restful import Resource, reqparse, fields, marshal
from app import api, app, db
from app.models import Photo


# Return all photos with a consistent URL
photo_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "upload_date": fields.Integer(),
    "public": fields.Boolean(),
    "uri": fields.Url("photo"),
}


class PhotoListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True, location="json")
        self.reqparse.add_argument(
            "upload_date", type=int, required=True, location="json"
        )
        self.reqparse.add_argument("public", type=bool, location="json")
        super(PhotoListAPI, self).__init__()

    # TODO: Return only public for non-logged in user
    def get(self):
        query = Photo.query.all()
        # Each record comes in as a Response object that needs
        # to be serialized for the return value.
        photos = [marshal(photo, photo_fields) for photo in query]
        return photos, 200

    # TODO: Convert to multipart-form input, not JSON
    def post(self):
        args = self.reqparse.parse_args()
        if not args:
            abort(jsonify(message=args), 400)

        # Write the photo to the DB
        # TODO: Save the image to the filesystem
        p = Photo(args["title"], args["upload_date"], args["public"])
        db.session.add(p)
        db.session.commit()

        return {"photo": marshal(p, photo_fields)}, 201


class PhotoAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, location="json")
        self.reqparse.add_argument("public", type=bool, location="json")
        super(PhotoAPI, self).__init__()

    def get(self, id):
        photo = Photo.query.get(id)
        if photo is None:
            return "Not found", 404
        return {"photo": marshal(photo, photo_fields)}, 200

    def put(self, id):
        photo = Photo.query.get(id)
        args = self.reqparse.parse_args()
        # Check for an empty argument object and return
        if args is not None:
            # Check that at least one value is not NoneType
            if not all(val is None for val in args.values()):
                for k, v in dict(args).items():
                    if v is not None:
                        photo.update(k, v)

                return {"photo": marshal(photo, photo_fields)}, 200
            else:
                abort(400)

    def delete(self, id):
        Photo.query.filter_by(id=id).delete()
        db.session.commit()
        return {"message": "Successfully deleted"}, 200


api.add_resource(PhotoListAPI, "/api/v1.0/photos", endpoint="photos")
api.add_resource(PhotoAPI, "/api/v1.0/photos/<id>", endpoint="photo")
