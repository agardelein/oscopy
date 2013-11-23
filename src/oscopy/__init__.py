from .signal import Signal
from .readers.reader import ReadError
from .writers.writer import WriteError
from .graphs import factors_to_names, abbrevs_to_factors, names_to_factors
from .figure import Figure
from .context import Context
import gobject
from .figure import MAX_GRAPHS_PER_FIGURE

gobject.type_register(signal.Signal)

