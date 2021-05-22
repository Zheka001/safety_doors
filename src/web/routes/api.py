# -*- coding: utf-8 -*-
from pathlib import Path
from uuid import uuid4
from flask import Blueprint
from flask_restful import Api, Resource, request

from src.utils.extracting import unzip


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


class VersionResource(Resource):
    @staticmethod
    def get():
        data_ = {'version': 0.1}
        return data_, 200


class ImageProcessingResource(Resource):
    def __init__(self, *args, **kwargs):
        super(ImageProcessingResource, self).__init__(*args, **kwargs)

    # @login_required
    def post(self):
        file = request.files['file']
        filename = self.save_file_to_disk(file)
        if filename is None:
            return {'message': 'invalid type of file'}, 404
        try:
            result = self.process(filename)
            return result, 200
        except Exception as e:
            return {'message': e}, 404

    def process(self, filename):
        print(filename)
        return {'alert': 1}

    def save_file_to_disk(self, file):
        if self.allowed_file(file.filename):
            filename = str(Path('db').joinpath(file.filename))
            file.save(Path('db').joinpath(file.filename))
            if filename[-3:] == 'zip':
                path_to_file = unzip(filename, str(Path(filename).parent))
                Path(filename).unlink()
                filename = path_to_file
            return filename
        return None

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename[-3:] in ['zip', 'pcb']


api.add_resource(VersionResource, '/version')
api.add_resource(ImageProcessingResource, '/api/1/image_processing')
