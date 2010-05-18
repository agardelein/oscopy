import IPython
from context import Context
from app import OscopyApp

_ctxt = Context()
_app = OscopyApp(_ctxt)
ip = IPython.ipapi.get()
    
def do_create(self, args):
    _app.do_create(args)

def do_destroy(self, args):
    _app.do_destroy(args)

def do_select(self, args):
    _app.do_select(self, args)

def do_layout(self, args):
    _app.do_layout(args)

def do_figlist(self, args):
    _app.do_figlist(args)

def do_plot(self, args):
    _app.do_plot(args)

def do_read(self, arg):
    _app.do_read(arg)

def do_write(self, arg):
    _app.do_write(arg)

def do_update(self, args):
    _app.do_update(args)

def do_add(self, args):
    _app.do_add(args)

def do_delete(self, args):
    _app.do_delete(args)

def do_mode(self, args):
    _app.do_mode(args)

def do_scale(self, args):
    _app.do_scale(args)

def do_range(self, args):
    _app.do_range(args)

def do_unit(self, args):
    _app.do_unit(args)

def do_insert(self, args):
    _app.do_insert(args)

def do_remove(self, args):
    _app.do_remove(args)

def do_freeze(self, args):
    _app.do_freeze(args)

def do_unfreeze(self, args):
    _app.do_unfreeze(args)

def do_siglist(self, args):
    _app.do_siglist(args)

def do_math(self, args):
    _app.do_math(args)

def do_exec(self, args):
    _app.do_exec(args)

def do_factors(self, args):
    _app.do_factors(args)

def init():
    ip.expose_magic('create', do_create)
    ip.expose_magic('destroy', do_destroy)
    ip.expose_magic('select', do_select)
    ip.expose_magic('layout', do_layout)
    ip.expose_magic('figlist', do_figlist)
    ip.expose_magic('plot', do_plot)
    ip.expose_magic('read', do_read)
    ip.expose_magic('write', do_write)
    ip.expose_magic('update', do_update)
    ip.expose_magic('add', do_add)
    ip.expose_magic('delete', do_delete)
    ip.expose_magic('mode', do_mode)
    ip.expose_magic('scale', do_scale)
    ip.expose_magic('range', do_range)
    ip.expose_magic('unit', do_unit)
    ip.expose_magic('insert', do_insert)
    ip.expose_magic('remove', do_remove)
    ip.expose_magic('freeze', do_freeze)
    ip.expose_magic('unfreeze', do_unfreeze)
    ip.expose_magic('siglist', do_siglist)
    ip.expose_magic('math', do_math)
    ip.expose_magic('exec', do_exec)
    ip.expose_magic('factors', do_factors)
