# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request

from app.models import OpRole


class RoleApi(Resource):
    def get(self, **kwargs):
        role = OpRole.find(**kwargs)
        if role:
            return {
                "message": 'role({}) found succeefully.'.format(role.name.encode('utf-8')),
                "data": role.to_json()
            }
        else:
            return {'message': 'role not found'}, 404

class RoleListApi(Resource):
    def get(self):
        roles = OpRole.query.all()
        if roles:
            return {
                'message': 'all roles listed.',
                'data': {
                    'count': len(roles),
                    'records': [
                        role.to_json() for role in roles
                    ]
                }
            }
        else:
            return {
                'message': 'no roles.'
            }, 204
