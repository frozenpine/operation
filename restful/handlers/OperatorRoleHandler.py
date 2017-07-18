from flask import request
from app import db
from app.models import Operator, OpRole
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from ..errors import DataNotJsonError, DataNotMatchError, DataUniqueError
from ..output import Output


class Operator2RoleApi(Resource):
    def __init__(self):
        super(Operator2RoleApi, self).__init__()

    def post(self, **kwargs):
        role = OpRole.find(**kwargs)
        if role is not None:
            try:
                id_list = request.get_json(force=True).get('id')
                name_list = request.get_json(force=True).get('login')
            except BadRequest:
                try:
                    raise DataNotJsonError
                except DataNotJsonError:
                    return Output(DataNotJsonError())
            else:
                try:
                    if name_list is not None:
                        for x in name_list:
                            operator = Operator.query.filter_by(login=x).first()
                            if operator is not None:
                                if operator in role.users.all():
                                    raise DataUniqueError
                                operator.roles.append(role)
                                role.users.append(operator)
                            else:
                                raise DataNotMatchError
                    if id_list is not None:
                        for x in id_list:
                            operator = Operator.query.filter_by(id=x).first()
                            if operator is not None:
                                if operator in role.users.all():
                                    raise DataUniqueError
                                operator.roles.append(role)
                                role.users.append(operator)
                            else:
                                raise DataNotMatchError
                except DataUniqueError:
                    return Output(DataUniqueError())
                except DataNotMatchError:
                    return Output(DataNotMatchError())
                else:
                    db.session.add(role)
                    db.session.commit()
                    return Output(role)
        else:
            return {'message': 'Not found.'}, 404


class Role2OperatorApi(Resource):
    def __init__(self):
        super(Role2OperatorApi, self).__init__()

    def post(self, **kwargs):
        operator = Operator.find(**kwargs)
        if operator is not None:
            try:
                id_list = request.get_json(force=True).get('id')
                name_list = request.get_json(force=True).get('name')
            except BadRequest:
                try:
                    raise DataNotJsonError
                except DataNotJsonError:
                    return Output(DataNotJsonError())
            else:
                try:
                    if name_list is not None:
                        for x in name_list:
                            role = OpRole.query.filter_by(name=x).first()
                            if role is not None:
                                if role in operator.roles.all():
                                    raise DataUniqueError
                                operator.roles.append(role)
                                role.users.append(operator)
                            else:
                                raise DataNotMatchError
                    if id_list is not None:
                        for x in id_list:
                            role = OpRole.query.filter_by(id=x).first()
                            if role is not None:
                                if role in operator.roles.all():
                                    raise DataUniqueError
                                operator.roles.append(role)
                                role.users.append(operator)
                            else:
                                raise DataNotMatchError
                except DataUniqueError:
                    return Output(DataUniqueError())
                except DataNotMatchError:
                    return Output(DataNotMatchError())
                else:
                    db.session.add(operator)
                    db.session.commit()
                    return Output(operator)
        else:
            return {'message': 'Not found.'}, 404
