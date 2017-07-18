# -*- coding: UTF-8 -*-
from app.models import SQLModelMixin
from .errors import ApiError

class RestProtocol(dict):
    version = '1.0'

    def __init__(self, obj=None, **kwargs):
        super(RestProtocol, self).__init__()
        if isinstance(obj, SQLModelMixin):
            self['error_code'] = kwargs.get('error_code', 0)
            self['message'] = kwargs.get('message', '')
            self['data'] = obj.to_json()
        elif isinstance(obj, list):
            self['error_code'] = kwargs.get('error_code', 0)
            self['message'] = kwargs.get('message', '')
            self['data'] = {
                'count': len(obj),
                'records': [element.to_json() for element in obj]
            }
        elif isinstance(obj, dict):
            self['error_code'] = kwargs.get('error_code', 0)
            self['message'] = kwargs.get('message', '')
            self['data'] = obj
        elif isinstance(obj, ApiError):
            self['error_code'] = obj.error_code
            self['message'] = obj.message
            self['data'] = None
        elif not obj:
            self['error_code'] = kwargs.get('error_code', 0)
            self['message'] = kwargs.get('message', '')
            self['data'] = kwargs.get('data')
