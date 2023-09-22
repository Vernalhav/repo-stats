class callback:
    args_cache = {}

    def __init__(self, *args, **kwargs):
        self.args = (args, kwargs)

    def __call__(self, f):
        callback.args_cache[f.__name__] = self.args
        return f


def apply_callbacks(obj):
    for f, (args, kwargs) in callback.args_cache.items():
        bound_method = getattr(obj, f)
        obj.app.callback(*args, **kwargs)(bound_method)
