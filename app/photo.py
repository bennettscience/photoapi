import os
import werkzeug
from werkzeug.utils import secure_filename
from flask import make_response, jsonify, abort, request, Response, send_from_directory
from flask_restful import Resource, reqparse, fields, marshal, inputs
from app import api, app, db
from app.models import Photo
from datetime import datetime


# Return all photos with a consistent URL
photo_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "upload_date": fields.Integer(),
    "public": fields.Boolean(),
    "uri": fields.Url("photo"),
    "filename": fields.String()
}


class PhotoListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True, location="form")
        self.reqparse.add_argument(
            "upload_date", type=str, location="form"
        )
        self.reqparse.add_argument("public", type=inputs.boolean, location="form")
        self.reqparse.add_argument("file", type=werkzeug.datastructures.FileStorage, location='files')
        super(PhotoListAPI, self).__init__()

    # TODO: Return only public for non-logged in user
    def get(self):
        query = Photo.query.all()
        # Each record comes in as a Response object that needs
        # to be serialized for the return value.
        photos = [marshal(photo, photo_fields) for photo in query]
        return photos, 200

    def post(self):
        args = self.reqparse.parse_args()
        if not args:
            abort(400)

        if 'file' not in request.files:
            abort(400)

        upload_file = request.files['file']
        if upload_file.filename == '':
            abort(400)

        if upload_file and self.allowed_filename(upload_file.filename):
            filename = secure_filename(upload_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            upload_file.save(file_path)
            p = Photo(args["title"], args["upload_date"], args["public"], filename)
            db.session.add(p)
            db.session.commit()

            return marshal(p, photo_fields), 201

    @staticmethod
    def allowed_filename(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
        return marshal(photo, photo_fields), 200

    def put(self, id):
        if id is None:
            abort(400)
        photo = Photo.query.get(id)
        args = self.reqparse.parse_args()
        # Check for an empty argument object and return
        if args is not None:
            # Check that at least one value is not NoneType
            if not all(val is None for val in args.values()):
                for k, v in dict(args).items():
                    if v is not None:
                        photo.update(k, v)

                return marshal(photo, photo_fields), 200
            else:
                abort(400)

    def delete(self, id):
        photo = Photo.query.filter_by(id=id).first()
        # Get the file_path as a variable before deletion
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
        db.session.delete(photo)
        db.session.commit()

        return {"message": "Successfully deleted"}, 200


class PhotoFile(Resource):
    def get(self, filename):
        root_dir = os.path.dirname(os.getcwd())
        print(os.path.join(root_dir, 'static', 'uploads'))
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


api.add_resource(PhotoListAPI, "/api/v1.0/photos", endpoint="photos")
api.add_resource(PhotoAPI, "/api/v1.0/photos/<id>", endpoint="photo")
api.add_resource(PhotoFile, "/static/uploads/<path:filename>")
