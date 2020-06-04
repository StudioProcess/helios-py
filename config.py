import json
import time
import os.path
import re
try: from inotify_simple import INotify, flags
except: pass

class Config():
    '''Simple wrapper for a dict.
    Allows read access to dict via item access `config['key']` and attribute access `config.key`.
    Implements iteration as well as mebership test operators.
    '''
    def __init__(self, init_dict = {}):
        if type(init_dict) is dict: self.dict = init_dict
        else: self.dict = {}
    def __getitem__(self, key):
        return self.dict[key]
    def __getattr__(self, name):
        return self.dict[name]
    def __iter__(self):
        return self.dict.__iter__()
    def __contains__(self, item):
        return self.dict.__contains__(item)
    def __repr__(self):
        return f'Config({self.dict.__repr__()})'

_config_file = None
_config = {}
_default_config = None
_inotify = None
_wd = None
_last_check = None

def _update_config():
    global _config
    try:
        new_config = {}
        new_config.update(_default_config)
        with open(_config_file, 'r') as file:
            text = file.read()
        text = re.sub(r'\s*(//|#).*$', '', text, flags=re.MULTILINE)
        new_config.update( json.loads(text) )
        if new_config != _config: # only update if config has changed (this is actually a recursive dict comparison)
            _config.clear()
            _config.update(new_config)
            print('Loaded', _config_file, _config)
    except Exception as e:
        print('Error loading', _config_file, e)

def load(config_file, default_config = {}):
    global _config_file, _default_config, _inotify, _wd
    _config_file = config_file
    _default_config = default_config
    try:
        _inotify = INotify()
    except:
        print("Notice: Couldn't load inotify. Config will be reloaded with every call to update()");
        
    dir = './' + os.path.dirname(config_file)
    if _inotify:
        _wd = _inotify.add_watch(dir, flags.CREATE | flags.MODIFY)
    _update_config()
    return Config(_config)

def update(min_secs = 0):
    global _last_check
    current_time = time.time()
    if _last_check is not None and current_time - _last_check < min_secs:
        # skip check if not enough time passed since last check
        return
    _last_check= current_time
    if _inotify:
        events = _inotify.read(0) # wait 0 seconds
        for e in events:
            if e.name == _config_file:
                _update_config()
    else:
        _update_config()
