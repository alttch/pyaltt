__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.8"


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
        for f in self._functions:
            try:
                f()
            except Exception as e:
                self.error(e)

    def error(self, e):
        if self.on_error:
            kwargs = self.on_error_kwargs.copy()
            kwargs['e'] = e
            self.on_error(**kwargs)
        else:
            raise


class NamedFunctionCollecton(FunctionCollecton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._functions = {}

    def __call__(self, f=None):
        if f:
            self.append(f, '{}.{}'.format(f.__module__, f.__name__))
        else:
            return self.run()

    def append(self, f, name):
        self._functions[name] = f

    def remove(self, name):
        try:
            del self._functions[name]
        except Exception as e:
            self.error(e)

    def run(self):
        result = {}
        for name, f in self._functions.items():
            try:
                result[name] = f()
            except Exception as e:
                result[name] = str(e)
                self.error(e)
        return result
