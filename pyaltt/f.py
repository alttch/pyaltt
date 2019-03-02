__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.7"


class FunctionCollecton:

    def __init__(self, **kwargs):
        self.functions = set()
        self.on_error = kwargs.get('on_error')
        self.on_error_kwargs = kwargs.get('on_error_kwargs', {})

    def __call__(self, f):
        self.append(f)

    def append(self, f):
        self.functions.add(f)

    def remove(self, f):
        try:
            self.functions.remove(f)
        except Exception as e:
            self.error(e)

    def run(self):
        for f in self.functions:
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


class NamedFunctionCollecton:

    def __init__(self, **kwargs):
        self.functions = {}
        self.on_error = kwargs.get('on_error')
        self.on_error_kwargs = kwargs.get('on_error_kwargs', {})

    def __call__(self, f):
        self.append(f, '{}.{}'.format(f.__module__, f.__name__))

    def append(self, f, name):
        self.functions[name] = f

    def remove(self, name):
        try:
            del self.functions[name]
        except Exception as e:
            self.error(e)

    def run(self):
        result = {}
        for name, f in self.functions.items():
            try:
                result[name] = f()
            except Exception as e:
                result[name] = str(e)
                self.error(e)
        return result

    def error(self, e):
        if self.on_error:
            kwargs = self.on_error_kwargs.copy()
            kwargs['e'] = e
            self.on_error(**kwargs)
        else:
            raise
