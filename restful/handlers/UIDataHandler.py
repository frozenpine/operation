# -*- coding: UTF-8 -*-
from os import path
from sys import argv
from app.models import Server, TradeSystem, SystemType
from flask import url_for, request, redirect
from flask_restful import Resource

class UIDataApi(Resource):
    def get(self, name):
        if hasattr(self, name):
            return getattr(self, name)()
        else:
            return {'message': 'resource not found.'}, 404

    def sideBarCtrl(self):
        systems = TradeSystem.query.filter(TradeSystem.parent_sys_id == None).all()
        rtn = []
        for sys in systems:
            system = {
                'id': sys.id,
                'icon': 'am-icon-table',
                'name': sys.name,
                'desc': sys.description,
                'isSecond': len(sys.operation_groups) > 0,
                'isShow': False,
                'Url': '#statics/{}'.format(sys.id),
                'secondName': [
                    {
                        'id': group.id,
                        'name': group.name,
                        'Url': '#op_group/{}'.format(group.id)
                    } for group in sys.operation_groups]
            }
            rtn.append(system)
        return rtn

    def map(self):
        try:
            name = request.values['name']
        except KeyError:
            return {
                'message': 'no name specified.'
            }, 404
        uri = url_for('static', filename='json/map/{}.json'.format(name))
        base_path = path.dirname(argv[0])
        abs_path = path.join(base_path, 'app{}'.format(uri))
        if path.isfile(abs_path):
            return redirect(uri)
        else:
            return {
                'message': 'no map data for {}.'.format(name)
            }, 404

    def idc(self):
        return [
            {'name': u'上海', 'value': [121.48, 31.22, 20]},
            {'name': u'大连', 'value': [121.46, 39.03, 15]},
            {'name': u'郑州', 'value': [113.65, 34.76, 10]},
        ]

    def relation(self):
        office = [{
            'name': '办公系统'
        }, {
            'name': 'confluence',
            'category': 'System'
        }, {
            'name': 'jira',
            'category': 'System'
        }]
        qdiam = [{
            'name': 'QDIAM'
        }, {
            'name': '行情子系统',
            'category': 'System'
        }, {
            'name': '交易子系统',
            'category': 'System'
        }, {
            'name': '风控子系统',
            'category': 'System'
        }, {
            'name': '柜台子系统',
            'category': 'System'
        }, {
            'name': 'qmarket 1',
            'category': 'Process'
        }, {
            'name': 'qmarket 2',
            'category': 'Process'
        }, {
            'name': 'qicegateway 1',
            'category': 'Process'
        }, {
            'name': 'qicegateway 2',
            'category': 'Process'
        }, {
            'name': 'qtrade',
            'category': 'Process'
        }, {
            'name': 'qdata',
            'category': 'Process'
        }, {
            'name': 'qquery',
            'category': 'Process'
        }, {
            'name': 'qmdb',
            'category': 'Process'
        }, {
            'name': 'qsdb',
            'category': 'Process'
        }, {
            'name': 'mysql',
            'category': 'Process'
        }, {
            'name': 'tomcat',
            'category': 'Process'
        }]
        kvm = [{
            'name': 'KVM'
        }, {
            'name': 'nas26',
            'category': 'System'
        }, {
            'name': 'kvm23',
            'category': 'System'
        }]

        kvmLink = [{
            'source': 'KVM',
            'target': 'kvm23'
        }, {
            'source': 'KVM',
            'target': 'nas26'
        }]
        officeLink = [{
            'source': '办公系统',
            'target': 'confluence'
        }, {
            'source': '办公系统',
            'target': 'jira'
        }]
        qdiamLink = [{
            'source': 'QDIAM',
            'target': '行情子系统'
        }, {
            'source': 'QDIAM',
            'target': '交易子系统'
        }, {
            'source': 'QDIAM',
            'target': '风控子系统'
        }, {
            'source': 'QDIAM',
            'target': '柜台子系统'
        }, {
            'source': '行情子系统',
            'target': 'qmarket 1'
        }, {
            'source': '行情子系统',
            'target': 'qmarket 2'
        }, {
            'source': '风控子系统',
            'target': 'qicegateway 1'
        }, {
            'source': '风控子系统',
            'target': 'qicegateway 2'
        }, {
            'source': '交易子系统',
            'target': 'qtrade'
        }, {
            'source': '交易子系统',
            'target': 'qdata'
        }, {
            'source': '交易子系统',
            'target': 'qquery'
        }, {
            'source': '交易子系统',
            'target': 'qmdb'
        }, {
            'source': '交易子系统',
            'target': 'qsdb'
        }, {
            'source': '柜台子系统',
            'target': 'mysql'
        }, {
            'source': '柜台子系统',
            'target': 'tomcat'
        }]
        option = {
            'backgroundColor': '#fff',
            'title': {
                'text': "系统关系图",
                'top': "top",
                'left': "center"
            },
            'legend': [{
                'tooltip': {
                    'show': True
                },
                'selectedMode': 'false',
                'bottom': 20,
                'data': ['KVM', 'QDIAM', '办公系统', 'System', 'Process']
            }],
            'toolbox': {
                'show': True,
                'feature': {
                    'dataView': {'show': True, 'readOnly': True},
                    'restore': {'show': True}
                }
            },
            'animationDuration': 3000,
            'animationEasingUpdate': 'quinticInOut',
            'series': [{
                'name': 'KVM',
                'type': 'graph',
                'layout': 'force',
                'force': {
                    'initLayout': 'circular',
                    'repulsion': [30, 100],
                    'gravity': 0.6,
                    'edgeLength': [30, 100],
                },
                'draggable': True,
                'data': kvm,
                'links': kvmLink,
                'edgeSymbol': ['', 'arrow'],
                'categories': [
                    {'name': 'System'},
                    {'name': 'Process'}
                ],
                'focusNodeAdjacency': True,
                'roam': True,
                'label': {
                    'normal': {
                        'show': True,
                        'position': 'top'
                    }
                },
                'lineStyle': {
                    'normal': {
                        'color': 'source',
                        'curveness': 0.3,
                        'type': "solid"
                    }
                }
            }, {
                'name': '办公系统',
                'type': 'graph',
                'layout': 'force',
                'force': {
                    'repulsion': 100,
                    'gravity': 0.1,
                    'edgeLength': 100,
                },
                'draggable': True,
                'data': office,
                'links': officeLink,
                'edgeSymbol': ['', 'arrow'],
                'categories': [
                    {'name': 'System'},
                    {'name': 'Process'}
                ],
                'focusNodeAdjacency': True,
                'roam': True,
                'label': {
                    'normal': {
                        'show': True,
                        'position': 'top'
                    }
                },
                'lineStyle': {
                    'normal': {
                        'color': 'source',
                        'curveness': 0.3,
                        'type': "solid"
                    }
                }
            }, {
                'name': 'QDIAM',
                'type': 'graph',
                'layout': 'force',
                'force': {
                    'repulsion': 100,
                    'gravity': 0.1,
                    'edgeLength': 100,
                },
                'draggable': True,
                'data': qdiam,
                'links': qdiamLink,
                'edgeSymbol': ['', 'arrow'],
                'categories': [
                    {'name': 'System'},
                    {'name': 'Process'}
                ],
                'focusNodeAdjacency': True,
                'roam': True,
                'label': {
                    'normal': {
                        'show': True,
                        'position': 'top'
                    }
                },
                'lineStyle': {
                    'normal': {
                        'color': 'source',
                        'curveness': 0.3,
                        'type': "solid"
                    }
                }
            }]
        }
        return option
