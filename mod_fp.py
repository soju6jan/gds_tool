from .setup import *


class ModuleFP(PluginModuleBase):

    def __init__(self, P):
        super(ModuleFP, self).__init__(P, name='fp', first_menu='setting')
        self.db_default = {
            f'{self.name}_db_version' : '3',
            f'{self.name}_use_plexscan' : 'False',
            f'{self.name}_ignore_rule' : '',
            f'{self.name}_change_rule' : '',
            f'fp_item_last_list_option' : '',
        }
        self.web_list_model = ModelFPItem

    def process_discord_data(self, data):
        #P.logger.warning(d(data))
        try:
            db_item = ModelFPItem.process_discord_data(data)

            if P.ModelSetting.get_bool(f'{self.name}_use_plexscan') == False:
                return
            ignore_list = P.ModelSetting.get_list(f'{self.name}_ignore_rule')
            for ignore in ignore_list:
                if ignore in db_item.gds_path:
                    db_item.status = 'IGNORE'
                    db_item.save()
                    return
            change_list = P.ModelSetting.get_list(f'{self.name}_change_rule')
            ret = db_item.gds_path
            for rule in change_list:
                tmp = rule.split('|')
                ret = ret.replace(tmp[0].strip(), tmp[1].strip())
            if ret[0] != '/':
                ret = ret.replace('/', '\\')

            db_item.local_path = ret

            PP = F.PluginManager.get_plugin_instance('plex_mate')
            PP.ModelScanItem(ret, mode="ADD", callback_id=f"gds_tool_{db_item.id}", callback_url=ToolUtil.make_apikey_url("/gds_tool/api/fp/scan_completed")).save()
            db_item.status = "SCAN_REQUEST"
            db_item.save()
        except Exception as e: 
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())

    
    def process_api(self, sub, req):
        #P.logger.error(sub)
        #P.logger.error(d(req.form))
        try:
            callback_id = req.form['callback_id']
            db_item = ModelFPItem.get_by_id(callback_id.split('_')[-1])
            db_item.status = req.form['status']
            db_item.save()
            return jsonify({'ret':'success'})
        except Exception as e: 
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())



class ModelFPItem(ModelBase):
    P = P
    __tablename__ = 'fp_item'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = P.package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)

    mode = db.Column(db.String)
    data = db.Column(db.JSON)
    status = db.Column(db.String)
    gds_path = db.Column(db.String)
    local_path = db.Column(db.String)

    def __init__(self):
        self.created_time = datetime.now()
        self.status = 'READY'

    
    @classmethod
    def make_query(cls, req, order='desc', search='', option1='all', option2='all'):
        with F.app.app_context():
            query = db.session.query(cls)
            query = cls.make_query_search(F.db.session.query(cls), search, cls.gds_path)

            if option1 != 'all':
                query = query.filter(cls.mode == option1)
            if option2 != 'all':
                query = query.filter(cls.status.like(option2 + '%'))
            query = query.order_by(desc(cls.id)) if order == 'desc' else query.order_by(cls.id)
            return query  

    @classmethod
    def process_discord_data(cls, data):
        try:
            P.logger.error(data)
            db_item = ModelFPItem()
            if data['ch'] == 'bot_gds_vod':
                db_item.mode = 'VOD'
                db_item.data = data
                db_item.gds_path = data['msg']['data']['r_fold'] + '/' + data['msg']['data']['r_file']
            elif data['ch'] == 'bot_gds_movie':
                db_item.mode = 'MOVIE'
                db_item.data = data
                db_item.gds_path = data['msg']['data']['gds_path']
            db_item.save()
            return db_item
        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())   