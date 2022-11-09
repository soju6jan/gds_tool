from .setup import *
from support.expand.rclone import SupportRclone

class ModuleRequest(PluginModuleBase):

    def __init__(self, P):
        super(ModuleRequest, self).__init__(P, name='request', first_menu='setting')
        self.db_default = {
            f'{self.name}_db_version' : '1',
            f'{self.name}_remote_path' : '',
        }
        self.web_list_model = ModelRequestItem



    def process_normal(self, sub, req):
        try:
            if sub == 'copy_completed':
                clone_folder_id = req.form['clone_folder_id']
                client_db_id = req.form['client_db_id']
                logger.debug(f'copy_complted: {client_db_id}, {clone_folder_id}')
                self.do_download(client_db_id, clone_folder_id)
                ret = {'ret':'success'}
                return jsonify(ret)
            elif sub == 'callback':
                about = req.form['about']
                client_db_id = req.form['client_db_id']
                ret = req.form['ret']
                logger.debug('about : %s, client_db_id : %s, ret : %s', about, client_db_id, ret)
                if about == 'request':
                    item = ModelRequestItem.get_by_id(client_db_id)
                    item.status = req.form['ret']
                    item.save()
                ret = {'ret':'success'}
                return jsonify(ret)
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())









    def get_setting_remote_path(self, board_type, category_type):
        try:
            tmp = P.ModelSetting.get_list(f'{self.name}_remote_path')
            remote_list = {}
            for t in tmp:
                t2 = t.split('=')
                if len(t2) == 2 and t2[1].strip() != '':
                    remote_list[t2[0].strip()] = t2[1].strip()
            keys = [f"{board_type},{category_type}", board_type, 'default']

            for key in keys:
                if key in remote_list:
                    return remote_list[key]
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    
    def can_use_request(self, remote_path):
        try:
            size_data = SupportRclone.size('%s:{1PwFA8w365qiPHtVQpqy_qmkQmRtklT5x}' % remote_path.split(':')[0])
            if size_data['count'] == 1 and size_data['bytes'] == 7:
                return True
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
        return False


    def add_copy(self, source_id, folder_name, board_type, category_type, size, count, copy_type='folder', remote_path=None):
        P.logger.error(f"{source_id=}")
        P.logger.error(f"{folder_name=}")
        P.logger.error(f"{board_type=}")
        P.logger.error(f"{category_type=}")
        P.logger.error(f"{size=}")
        P.logger.error(f"{count=}")
        P.logger.error(f"{copy_type=}")
        P.logger.error(f"{remote_path=}")

        try:
            ret = {'ret':'fail', 'remote_path':remote_path, 'server_response':None}
            
            if ret['remote_path'] is None:
                ret['remote_path'] = self.get_setting_remote_path(board_type, category_type)
            if ret['remote_path'] is None:
                ret['ret'] = 'remote_path_is_none'
                return ret

            item = ModelRequestItem.get_by_source_id(source_id)
            if item is not None:
                ret['ret'] = 'already'
                ret['status'] = item.status
                return ret
            
            can_use_share_flag = self.can_use_request(ret['remote_path'])
            if not can_use_share_flag:
                ret['ret'] = 'cannot_access'
                return ret
            
            item = ModelRequestItem()
            item.copy_type = copy_type
            item.source_id = source_id
            item.target_name = folder_name
            item.board_type = board_type
            item.category_type = category_type
            item.size = size
            item.count = count
            item.remote_path = ret['remote_path']
            item.save()

            data = item.as_dict()

            data['ddns'] = F.SystemModelSetting.get('ddns')
            PP = F.PluginManager.get_plugin_instance('sjva')
            data['sjva_id'] = PP.ModelSetting.get('sjva_id')
            data['version'] = F.config['version']
            #url = F.config['define']['WEB_DIRECT_URL'] + '/server_tool/normal/gds/request'
            url = 'http://localhost:8888/server_tool/normal/gds/request'
            res = requests.post(url, data={'data':json.dumps(data)})
            ret['request_db_id'] = data['id']
            ret['server_response'] = res.json()
            if ret['server_response']['ret'] == 'enqueue':
                if 'db_id' in ret['server_response'] and ret['server_response']['queue_name'] is not None:
                    item.status = 'request'
                    item.request_time = datetime.now()
                    item.save()
                    ret['ret'] = 'success'
            else:
                item.status = ret['server_response']['ret']
                #item.request_time = datetime.now()
                #item.save()
                ret['ret'] = ret['server_response']['ret']

            
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret['ret'] = 'fail'
            ret['log'] = str(e)

        logger.debug(ret)
        return ret




    def do_download(self, db_id, clone_folder_id):
        def func():
            try:
                item = ModelRequestItem.get_by_id(int(db_id))
                if item is None:
                    logger.error('CRITICAL ERROR:%s', db_id)
                    return
                item.status = 'clone'
                item.clone_completed_time = datetime.now()
                item.clone_folderid = clone_folder_id
                #item.save()
                remote_path = item.remote_path
                
                try:
                    for i in range(5):
                        size_data = SupportRclone.size('%s:{%s}' % (remote_path.split(':')[0], clone_folder_id))
                        logger.debug('size_data : %s, %s', i, size_data)
                        if size_data is None or size_data['count'] == 0:
                            time.sleep(30)
                        else:
                            break
                except Exception as e: 
                    logger.error('Exception:%s', e)
                    logger.error(traceback.format_exc())

                source_remote = '{gdrive_remote}:{{{folderid}}}'.format(gdrive_remote=remote_path.split(':')[0], folderid=item.clone_folderid)

                ret = SupportRclone.chpar(source_remote, remote_path)

                if ret:
                    item.status = 'completed'
                    item.completed_time = datetime.now()
                else:
                    item.status = 'fail_move'
                    item.completed_time = datetime.now()
            except Exception as e: 
                logger.error('Exception:%s', e)
                logger.error(traceback.format_exc())
                item.status = 'fail_download_exception'
            finally:
                if item is not None:
                    item.save()
        thread = threading.Thread(target=func, args=())
        thread.setDaemon(True)
        thread.start()







class ModelRequestItem(ModelBase):
    P = P
    __tablename__ = 'request_item'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = P.package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)

    copy_type = db.Column(db.String) # folder, file
    source_id = db.Column(db.String)
    target_name = db.Column(db.String) # 폴더면 폴더명, 파일이면 파일명

    call_from = db.Column(db.String)
    board_type = db.Column(db.String)
    category_type = db.Column(db.String)
    remote_path = db.Column(db.String) 
    size = db.Column(db.Integer)
    count = db.Column(db.Integer)

    status = db.Column(db.String) # 'ready' 'request' 'clone' 'completed'
    clone_completed_time = db.Column(db.DateTime)
    completed_time = db.Column(db.DateTime)
    request_time = db.Column(db.DateTime)

    clone_folderid = db.Column(db.String) 


    def __init__(self):
        self.created_time = datetime.now()
        self.status = 'ready'

    @classmethod
    def get_by_source_id(cls, source_id):
        with F.app.app_context():
            return db.session.query(cls).filter_by(source_id=source_id).first()
    
    
    @classmethod
    def make_query(cls, req, order='desc', search='', option1='all', option2='all'):
        with F.app.app_context():
            query = db.session.query(cls)
            query = cls.make_query_search(F.db.session.query(cls), search, cls.target_name)

            if option1 != 'all':
                query = query.filter(cls.board_type == option1)
            if option2 != 'all':
                query = query.filter(cls.status.like(option2 + '%'))
            query = query.order_by(desc(cls.id)) if order == 'desc' else query.order_by(cls.id)
            return query  

