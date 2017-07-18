# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app.models import TradeSystem, ScriptType, OperationCatalog
from ..output import Output
from ..errors import DataNotMatchError


class SystemInformationApi(Resource):
    def __init__(self):
        super(SystemInformationApi, self).__init__()

    def get(self):
        systems = TradeSystem.query.all()
        return Output(systems)


class ParentSystemFindOperationBookApi(Resource):
    def __init__(self):
        super(ParentSystemFindOperationBookApi, self).__init__()

    def get(self, **kwargs):
        system = TradeSystem.find(**kwargs)
        if system:
            if system.parent_sys_id == None:
                sys_list = [system]
                for child_sys in system.child_systems:
                    sys_list.append(child_sys)
                ob_result = []
                for sys in sys_list:
                    for ob in sys.operation_book:
                        ob_result.append(dict(name=ob.name, book_id=ob.id, description=ob.description))
                return {'message': 'All data listed.',
                        'error_code': 0,
                        'data': {'count': len(ob_result),
                                 'records': ob_result}}
            else:
                return Output(DataNotMatchError('The system is not a parent system.'))
        else:
            return {'message': 'System not found.'}, 404


class AddOperationBookBaseInformationApi(Resource):
    def __init__(self):
        super(AddOperationBookBaseInformationApi, self).__init__()

    def get(self):
        script_type_name = {'Checker': '检查',
                            'Executor': '执行',
                            'Interactivator': '交互',
                            'Execute_Checker': '检查和执行',
                            'Interactive_Checker': '检查和交互'}
        script_types = ScriptType._member_names_
        systems = TradeSystem.query.all()
        catalogs = OperationCatalog.query.all()
        system_list = []
        for sys in systems:
            system_list.append(dict(sys_id=sys.id, sys_name=sys.name))
        catalog_list = []
        for cl in catalogs:
            catalog_list.append(dict(catalog_id=cl.id, catalog_name=cl.name))
        script_type_list = []
        for name in script_types:
            script_type_list.append(dict(alias=script_type_name[name], name=name))
        return {'message': 'All data listed',
                'error_code': 0,
                'data': {'systems': system_list, 'script_types': script_type_list,
                         'catalogs': catalog_list}}