from configparser import SafeConfigParser
import settings
import os

config = SafeConfigParser()
section = "PARAMETERS"

def initialize():
    if os.path.exists(settings.CONF_FILE_NAME):
        return
    try:
        config.add_section(section)
    except:
        pass
    write_conf({})

def write_conf(new_conf={}):
    config.read(settings.CONF_FILE_NAME)
    for k, v in settings.args_list.items():
        if new_conf.get(k):
            config.set(section, k, new_conf.get(k))
        else:
            config.set(section, k, str(v))

        with open(settings.CONF_FILE_NAME, 'w') as f:
            config.write(f)

def read_conf():
    config.read(settings.CONF_FILE_NAME)
    ret = {}
    arg_list = settings.args_list
    for k, _ in arg_list.items():
        ret[k] = config.get(section, k)
    return ret

initialize()