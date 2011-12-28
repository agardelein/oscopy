
from signal import Signal
from figure import Figure
from context import Context
from readers.reader import ReadError
from graphs import factors_to_names, abbrevs_to_factors, names_to_factors
import gobject
from figure import MAX_GRAPHS_PER_FIGURE

gobject.type_register(signal.Signal)

try:
    get_ipython()
except NameError:
    pass
else:
    import ioscopy
    ioscopy.init()
