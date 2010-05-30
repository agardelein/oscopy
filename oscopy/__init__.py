
from signal import Signal
from figure import Figure
from context import Context
from app import OscopyApp
from readers.reader import ReadError
from graphs import factors_to_names, abbrevs_to_factors, names_to_factors

GETTEXT_DOMAIN = 'oscopy'
import gettext
import locale

locale.setlocale(locale.LC_ALL, '')

gettext.bindtextdomain(GETTEXT_DOMAIN)
gettext.textdomain(GETTEXT_DOMAIN)

import __builtin__
__builtin__._ = gettext.gettext

import ioscopy

if __IPYTHON__:
    ioscopy.init()
