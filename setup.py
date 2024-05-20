setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': 'request',
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
                'uri': 'upload',
                'name': 'Share 업로드',
                'list': [
                    {'uri': 'setting', 'name': '설정'},
                    {'uri': 'action', 'name': '업로드'},
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

DEFINE_DEV = False
if os.path.exists(os.path.join(os.path.dirname(__file__), 'mod_route.py')):
    DEFINE_DEV = True

P = create_plugin_instance(setting)
try:
    from .mod_fp import ModuleFP
    from .mod_request import ModelRequestItem, ModuleRequest
    from .mod_upload import ModuleUpload

    if DEFINE_DEV:
        from .mod_route import ModuleRoute
    else:
        from support import SupportSC
        ModuleRoute = SupportSC.load_module_P(P, 'mod_route').ModuleRoute

    P.set_module_list([ModuleRoute, ModuleRequest, ModuleFP, ModuleUpload])
    P.ModelRequestItem = ModelRequestItem

    from support import SupportSC
    if DEFINE_DEV:
        from .worker import SupportRcloneWorker
        
        P.SupportRcloneWorker = SupportRcloneWorker
    else:
        P.SupportRcloneWorker = SupportSC.load_module_P(P, 'worker').SupportRcloneWorker
    P.SupportRcloneWorker.set_config_path(os.path.join(os.path.dirname(__file__), 'files', 'w.conf'))
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

P.add_copy = P.logic.get_module('request').add_copy

logger = P.logger
