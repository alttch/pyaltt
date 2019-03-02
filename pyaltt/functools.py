__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.0.3"


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
        except:
            self.error()

    def run(self):
        for f in self.functions:
            try:
                f()
            except:
                self.error()

    def error(self, e):
        if self.on_error:
            kwargs = self.on_error_kwargs.copy()
            kwargs['e'] = e
            self.on_error(**kwargs)
        else:
            raise
