# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app import db
from app.models import SystemVendor
from flask import request
from werkzeug.exceptions import BadRequest
from restful.errors import (DataNotJsonError,
                            DataUniqueError,
                            DataNotNullError,
                            ApiError)
from restful.protocol import RestProtocol


class VendorApi(Resource):
    def __init__(self):
        super(VendorApi, self).__init__()

    def get(self, **kwargs):
        sys_vendor = SystemVendor.find(**kwargs)
        if sys_vendor is not None:
            return RestProtocol(sys_vendor)
        else:
            return {'message': 'System vendor not found'}, 404

    def put(self, **kwargs):
        sys_vendor = SystemVendor.find(**kwargs)
        if sys_vendor:
            try:
                data = request.get_json(force=True)
                if data.get('name'):
                    if sys_vendor.name != data.get('name') and SystemVendor.find(name=data.get('name')):
                        raise DataUniqueError
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            except DataUniqueError as e:
                return RestProtocol(e)
            else:
                sys_vendor.name = data.get('name', sys_vendor.name)
                sys_vendor.contactors = data.get('contact', sys_vendor.contactors)
                sys_vendor.description = data.get('description', sys_vendor.description)
                db.session.add(sys_vendor)
                db.session.commit()
                return RestProtocol(sys_vendor)
        else:
            return {'message': 'System vendor not found'}, 404


class VendorListApi(Resource):
    def __init__(self):
        super(VendorListApi, self).__init__()
        self.not_null_list = ['name']

    def get(self):
        sys_vendors = SystemVendor.query.all()
        return RestProtocol(sys_vendors)

    def post(self):
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            if SystemVendor.find(name=data.get('name')):
                raise DataUniqueError
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        else:
            vendor = SystemVendor()
            vendor.name = data.get('name')
            vendor.contactors = data.get('contact')
            vendor.description = data.get('description')
            db.session.add(vendor)
            db.session.commit()
            return RestProtocol(vendor)




