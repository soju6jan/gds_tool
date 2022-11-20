setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': None,
    'menu': {
        'uri': __package__,
        'name': '구드공 툴',
        'list': [
            {
                'uri': 'request',
                'name': '복사 요청',
                'list': [
                    {'uri': 'setting', 'name': '설정'},
                    {'uri': 'request', 'name': '개별 요청'},
                    {'uri': 'list', 'name': '목록'},
                ]
            },
            {
                'uri': 'fp',
                'name': 'GDS 변경사항',
                'list': [
                    {'uri': 'setting', 'name': '설정'},
                    {'uri': 'list', 'name': '목록'},
                ]
            },
            {
                'uri': 'manual',
                'name': '매뉴얼',
                'list': [
                    {'uri':'README.md', 'name':'README.md'}
                ]
            },
            {
                'uri': 'log',
                'name': '로그',
            },
        ]
    },
    'setting_menu': None,
    'default_route': 'normal',
}


from plugin import *

P = create_plugin_instance(setting)
try:
    from .mod_fp import ModuleFP
    from .mod_request import ModelRequestItem, ModuleRequest
    from .mod_route import ModuleRoute
    P.set_module_list([ModuleRoute, ModuleRequest, ModuleFP])
    P.ModelRequestItem = ModelRequestItem
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

P.add_copy = P.logic.get_module('request').add_copy

logger = P.logger
