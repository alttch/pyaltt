__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.9"


class FunctionCollecton:

    def __init__(self, **kwargs):
        self._functions = set()
        self.on_error = kwargs.get('on_error')
        self.on_error_kwargs = kwargs.get('on_error_kwargs', {})

    def __call__(self, f=None):
        if f:
            self.append(f)
        else:
            return self.run()

    def append(self, f):
        self._functions.add(f)

    def remove(self, f):
        try:
            self._functions.remove(f)
        except Exception as e:
            self.error(e)

    def run(self):
        return self.execute()

    def execute(self):
        result = {}
        for f in self._functions:
            k = '{}.{}'.format(f.__module__, f.__name__)
            try:
                result[k] = f()
            except Exception as e:
                result[k] = str(e)
                self.error(e)
        return result

    def error(self, e):
        if self.on_error:
            kwargs = self.on_error_kwargs.copy()
            kwargs['e'] = e
            self.on_error(**kwargs)
        else:
            raise
