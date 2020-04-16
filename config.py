import json
import time
import os.path
from inotify_simple import INotify, flags

_config_file = None
_config = {}
_default_config = None
_inotify = None
_wd = None
_last_check = None

def _update_config():
    global _config
    _config.clear()
    _config.update(_default_config)
    try:
        with open(_config_file, 'r') as file:
            new_config = json.load(file)
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
    return _config

def update(min_secs = 3):
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
