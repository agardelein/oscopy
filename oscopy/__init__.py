
from signal import Signal
from figure import Figure
from context import Context
from readers.reader import ReadError
from graphs import factors_to_names, abbrevs_to_factors, names_to_factors
import gobject

gobject.type_register(signal.Signal)

try:
    __IPYTHON__
except NameError:
    pass
else:
    import ioscopy
    ioscopy.init()
