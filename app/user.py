from app import api
from flask_restful import Resource


class UserAPI(Resource):
    def get(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass

api.add_resource(UserAPI, "/photos/api/v1.0/user", endpoint="user")
