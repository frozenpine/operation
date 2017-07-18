# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app import db
from app.models import Operator
from flask import request
from werkzeug.exceptions import BadRequest
from werkzeug.security import check_password_hash
from restful.errors import DataNotJsonError, DataUniqueError, DataNotNullError, DataTypeError, DataNotMatchError
from restful.protocol import RestProtocol


class UserApi(Resource):
    def __init__(self):
        super(UserApi, self).__init__()

    def get(self, **kwargs):
        user = Operator.find(**kwargs)
        if user is not None:
            return RestProtocol(user)
        else:
            return {'message': 'Not found'}, 404

    def put(self, **kwargs):
        user = Operator.find(**kwargs)
        if user is not None:
            try:
                data = request.get_json(force=True)
            except BadRequest:
                try:
                    raise DataNotJsonError
                except DataNotJsonError:
                    return RestProtocol(DataNotJsonError())
            else:
                try:
                    if 'old_password' in data:
                        if check_password_hash(user.password_hash, data.get('old_password')):
                            user.name = data.get('name', user.name)
                            user.disabled = data.get('disabled', user.disabled)
                            if 'password' in data:
                                user.password = data.get('password')
                        else:
                            try:
                                raise DataNotMatchError
                            except DataNotMatchError:
                                return RestProtocol(DataNotMatchError('Old password must match.'))
                    else:
                        raise DataNotNullError
                except DataNotNullError:
                    return RestProtocol(DataNotNullError())
                except TypeError:
                    try:
                        raise DataTypeError
                    except DataTypeError:
                        return RestProtocol(DataTypeError())
                else:
                    db.session.add(user)
                    db.session.commit()
                    return RestProtocol(user)
        else:
            return {'message': 'Not found'}, 404


class UserListApi(Resource):
    def __init__(self):
        super(UserListApi, self).__init__()

    def get(self):
        users = Operator.query.all()
        return RestProtocol(users)

    def post(self):
        user = []
        result_list = []
        try:
            data_list = request.get_json(force=True).get('data')
        except BadRequest:
            try:
                raise DataNotJsonError
            except DataNotJsonError:
                return RestProtocol(DataNotJsonError())
        else:
            try:
                for i in xrange(len(data_list)):
                    if not data_list[i].get('login') or not data_list[i].get('password'):
                        raise DataNotNullError
                    elif Operator.query.filter_by(login=data_list[i].get('login')).first() is not None:
                        raise DataUniqueError
                    x = Operator(login=data_list[i].get('login'),
                                 name=data_list[i].get('name'),
                                 password=data_list[i].get('password'))
                    user.append(x)
            except DataNotNullError:
                return RestProtocol(DataNotNullError())
            except DataUniqueError:
                return RestProtocol(DataUniqueError())
            except TypeError:
                try:
                    raise DataTypeError
                except DataTypeError:
                    return RestProtocol(DataTypeError())
            else:
                db.session.add_all(user)
                db.session.commit()
                for j in xrange(len(user)):
                    result_list.append(RestProtocol(user[j]))
                return result_list
