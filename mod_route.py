import requests
from flask import Response

from support_site import SupportWavve

from .setup import *


class ModuleRoute(PluginModuleBase):

    def __init__(self, P):
        super(ModuleRoute, self).__init__(P, name='route')
    
    

    def process_api(self, sub, req):
        if sub == 'streaming':
            PP = F.PluginManager.get_plugin_instance('sjva')
            sjva_id = PP.ModelSetting.get('sjva_id')
            url = f"{F.config['DEFINE']['WEB_DIRECT_URL']}/ff/ff_gds_play_two.php?type=file&id={request.args.get('id')}&user_id={sjva_id}&user_apikey={F.SystemModelSetting.get('apikey')}"
            #P.logger.error(url)
            data = requests.get(url).json()['data']
            req_headers = dict(request.headers)
            headers = {}
            if 'Range' not in req_headers or req_headers['Range'].startswith('bytes=0-'):
                headers['Range'] = "bytes=0-1048576"
            else:
                headers['Range'] = req_headers['Range']
            headers['Authorization'] = f"Bearer {data['token']}"
            headers['Connection'] = 'keep-alive'
            r = requests.get(data['url'], headers=headers, stream=True)
            rv = Response(r.iter_content(chunk_size=1048576), r.status_code, content_type=r.headers['Content-Type'], direct_passthrough=True)
            rv.headers.add('Content-Range', r.headers.get('Content-Range'))
            return rv