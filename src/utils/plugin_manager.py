import os
import traceback
from logging import getLogger
from importlib import import_module
from src.utils.plugin_obj import Plugin
from typing import Dict

log = getLogger('PluginManager')

def load_plugins_legacy():
    files = os.listdir('src/plugins')
    return [
        __import__(f'src.plugins.{x.removesuffix('.py')}')
        for x in files
        if not x.startswith("__") and x.endswith(".py")
    ]


def load_plugins():
    plugins: Dict[str, Plugin] = {}
    for file in os.listdir('src/plugins'):
        if file.startswith('__'):
            continue
        
        file_name = file.removesuffix('.py')
        try:
            log.info(f'Loading plug-in {file_name}')
            mod = import_module(f'src.plugins.{file_name}')
            cur_mod_obj = Plugin(mod)
            plugins[mod.__name__] = cur_mod_obj
            log.info(f'Plug-in {file_name} loaded successfully') 
        except ModuleNotFoundError:
            log.error(f'Plugin {file_name} not found!')
            log.error(traceback.format_exc())
        except Exception:
            log.error(f'Plugin {file_name} failed to load!')
            log.error(traceback.format_exc())
    print(plugins)
    list(plugins.items())[-1][1].is_active = False
    return plugins


plugins = load_plugins()