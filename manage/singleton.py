def singleton(obj_init):
    _instances = {}

    def _singleton(*args, **kwargs):
        if obj_init not in _instances.keys():
            _instances[obj_init] = obj_init(*args, **kwargs)
        return _instances[obj_init]

    return _singleton
