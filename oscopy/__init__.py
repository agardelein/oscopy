
from signal import Signal
from figure import Figure
from context import Context
from readers.reader import ReadError
from graphs import factors_to_names, abbrevs_to_factors, names_to_factors
import gobject

GETTEXT_DOMAIN = 'oscopy'
import gettext
import locale

locale.setlocale(locale.LC_ALL, '')

gettext.bindtextdomain(GETTEXT_DOMAIN)
gettext.textdomain(GETTEXT_DOMAIN)

import __builtin__
__builtin__._ = gettext.gettext

gobject.type_register(signal.Signal)

try:
    __IPYTHON__
except NameError:
    pass
else:
    import ioscopy
    ioscopy.init()
