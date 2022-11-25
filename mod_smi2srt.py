from .setup import *
from .support_smi2srt import SupportSmi2srt

name = 'smi2srt'

class ModuleSmi2srt(PluginModuleBase):
    
    def __init__(self, P):
        super(ModuleSmi2srt, self).__init__(P, name=name, first_menu='list', scheduler_desc="smi2srt 자막 변환")
        self.db_default = {
            f'{self.name}_db_version' : '1',
            f'{self.name}_auto_start' : 'False',
            f'{self.name}_interval' : '60',
            f'{self.name}_db_delete_day' : '30',
            f'{self.name}_db_auto_delete' : 'False',
            f'smi2srt_item_last_list_option': '',

            f'{self.name}_work_path' : '',
            f'{self.name}_flag_remake' : 'False',
            f'{self.name}_flag_remove_smi' : 'True',
            f'{self.name}_flag_append_ko' : 'True',
            f'{self.name}_flag_change_ko_srt' : 'True',
            f'{self.name}_fail_file_move' : 'False',
            f'{self.name}_fail_move_path' : '',
            f'{self.name}_not_smi_move_path' : '',
        }
        self.web_list_model = ModelSmi2srtItem

    def process_menu(self, sub, req):
        arg = P.ModelSetting.to_dict()
        if sub == 'setting':
            arg['is_include'] = F.scheduler.is_include(self.get_scheduler_name())
            arg['is_running'] = F.scheduler.is_running(self.get_scheduler_name())
        return render_template(f'{P.package_name}_{self.name}_{sub}.html', arg=arg)
      

    def scheduler_function(self):
        self.start_celery(Task.start, None, *(None,))


class Task:
    @staticmethod
    @F.celery.task
    def start(work_path):
        try:
            if work_path is None:
                work_paths = P.ModelSetting.get_list(f'{name}_work_path', ',')
            else:
                work_paths = [x.strip() for x in work_path.split(',')]
            logger.debug('start_by_path : %s', work_paths)
            fail_move_path = P.ModelSetting.get(f'{name}_fail_move_path') if P.ModelSetting.get_bool(f'{name}_fail_file_move') and P.ModelSetting.get(f'{name}_fail_move_path') != '' else ''
            not_smi_move_path = P.ModelSetting.get(f'{name}_not_smi_move_path') if P.ModelSetting.get_bool(f'{name}_fail_file_move') and P.ModelSetting.get(f'{name}_not_smi_move_path') != '' else ''
            for work_path in work_paths:
                result = SupportSmi2srt.start(work_path, 
                    remake=P.ModelSetting.get_bool(f'{name}_flag_remake'),
                    no_remove_smi=not P.ModelSetting.get_bool(f'{name}_flag_remove_smi'), 
                    no_append_ko=not P.ModelSetting.get_bool(f'{name}_flag_append_ko'), 
                    no_change_ko_srt=not P.ModelSetting.get_bool(f'{name}_flag_change_ko_srt'), 
                    fail_move_path=fail_move_path, not_smi_move_path=not_smi_move_path)
                #P.logger.debug(d(result))
                ModelSmi2srtItem.list_save(result) 
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())


class ModelSmi2srtItem(ModelBase):
    P = P
    __tablename__ = 'smi2srt_item'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = P.package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    
    change_type = db.Column(db.String)
    smi_file = db.Column(db.String)
    result = db.Column(db.String)
    data = db.Column(db.JSON)

    def __init__(self, result):
        self.created_time = datetime.now()
        if 'log' in result:
            result['log'] = result['log'].replace('<', '&lt;').replace('>', '&gt;')
        self.change_type = 'smi'
        self.created_time = datetime.now()
        self.smi_file = result['smi_file']
        self.result = result['ret']
        self.data = result


    @classmethod
    def list_save(cls, ret):
        try:
            with F.app.app_context():
                for item in ret['list']:
                    #logger.debug(d)
                    db_item = db.session.query(cls).filter_by(smi_file=item['smi_file']).delete()
                    new_db_item = ModelSmi2srtItem(item)
                    F.db.session.add(new_db_item)
                F.db.session.commit()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc()) 



    @classmethod
    def make_query(cls, req, order='desc', search='', option1='all', option2='all'):
        with F.app.app_context():
            query = db.session.query(cls)
            query = cls.make_query_search(query, search, cls.smi_file)
            if option1 != 'all':
                query = query.filter(cls.result == option1)
            if order == 'desc':
                query = query.order_by(desc(cls.id))
            else:
                query = query.order_by(cls.id)
            return query 

