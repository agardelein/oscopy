from Gnucap import *
from Signal import *

def load(args):
    obj = Gnucap()
    slist = obj.loadfile(args)
    print args, ":"
    for ns in slist:
        print ns.name, "/", ns.domain
