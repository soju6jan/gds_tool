import requests
from flask import Response

from support_site import SupportWavve

from .setup import *


class ModuleRoute(PluginModuleBase):

    def __init__(self, P):
        super(ModuleRoute, self).__init__(P, name='route')
    
    

    def process_api(self, sub, req):
        if sub == 'streaming' or sub == 'streaming.mp4':
            PP = F.PluginManager.get_plugin_instance('sjva')
            sjva_id = PP.ModelSetting.get('sjva_id')
            url = f"{F.config['DEFINE']['WEB_DIRECT_URL']}/ff/ff_gds_play_two.php?type=file&id={request.args.get('id')}&user_id={sjva_id}&user_apikey={F.SystemModelSetting.get('apikey')}"
            P.logger.error(url)
            data = requests.get(url).json()['data']
            req_headers = dict(request.headers)
            headers = {}
            #if 'Range' not in req_headers or req_headers['Range'].startswith('bytes=0-'):
            # by orial 
            # 구드공 툴의 재생기능에 mod_route.py 에 Range 헤더 처리 관련해서 IOS 에서 재생시 Range: bytes=0-1 로 요청해서 재생이 안되는 문제가 있네요.
            # startswith('bytes=0-') 으로 걸려있는 조건을 req_headers['Range'] == 'bytes=0-' 으로 정확히 체크하도록  수정해야 될거 같습니다.
            if 'Range' not in req_headers or req_headers['Range'] == 'bytes=0-':
                headers['Range'] = "bytes=0-1048576"
            else:
                headers['Range'] = req_headers['Range']
            headers['Authorization'] = f"Bearer {data['token']}"
            headers['Connection'] = 'keep-alive'
            r = requests.get(data['url'], headers=headers, stream=True)
            rv = Response(r.iter_content(chunk_size=1048576), r.status_code, content_type=r.headers['Content-Type'], direct_passthrough=True)
            rv.headers.add('Content-Range', r.headers.get('Content-Range'))
            return rv