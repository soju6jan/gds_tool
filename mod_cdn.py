import base64

from .setup import *


class ModuleCdn(PluginModuleBase):
    
    def __init__(self, P):
        super(ModuleCdn, self).__init__(P, name='cdn', first_menu='image')
        self.db_default = {
            f'{self.name}_db_version' : '1',
            f'{self.name}_foldername' : 'admin - TEST',
            f'{self.name}_folderid' : '',
        }


    def process_command(self, command, arg1, arg2, arg3, req):
        try:
            from . import SSGDrive
            ret = {'ret':'success'}
            if command == 'upload':
                filepath = os.path.join(F.config['path_data'], 'tmp', str(time.time()))
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(req.form['url'].split('base64,')[1]))
                    f.close()
                
                tmp = SSGDrive.upload_from_path(filepath, folderid=P.ModelSetting.get(f'{self.name}_folderid'))
                if tmp != None:
                    ret['url'] = tmp
                else:
                    ret['msg'] = '실패'
                    ret['ret'] = 'error'
            elif command == 'upload_http':
                tmp = SSGDrive.upload_from_url(arg1, folderid=P.ModelSetting.get(f'{self.name}_folderid'))
                if tmp != None:
                    ret['url'] = tmp
                else:
                    ret['msg'] = '실패'
                    ret['ret'] = 'error'
        except Exception as e: 
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())
            ret['ret'] = 'error'
            ret['msg'] = str(e)
        return jsonify(ret)
    