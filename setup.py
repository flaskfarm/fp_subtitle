setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': None,
    'menu': {
        'uri': __package__,
        'name': '자막 툴',
        'list': [
            {
                'uri': 'smi2srt',
                'name': '.smi to .srt',
                'list': [
                    {'uri': 'setting', 'name': '설정'},
                    {'uri': 'list', 'name': '처리 결과'},
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
    from .mod_smi2srt import ModuleSmi2srt
    P.set_module_list([ModuleSmi2srt])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

logger = P.logger
