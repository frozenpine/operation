# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app.models import OperationCatalog
from flask import request
from werkzeug.exceptions import BadRequest
from app import db
from ..errors import DataNotJsonError, DataNotNullError
from ..protocol import RestProtocol


class OperationCatalogApi(Resource):
    def __init__(self):
        super(OperationCatalogApi, self).__init__()

    def get(self):
        pass

    def put(self):
        pass




class OperationCatalogListApi(Resource):
    def __init__(self):
        super(OperationCatalogListApi, self).__init__()

    def get(self):
        op_catalogs = OperationCatalog.query.all()
        return RestProtocol(op_catalogs)

    def post(self):
        pass
