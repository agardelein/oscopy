""" Points list of a signal

A Signal is the common point between the reader and the graph objects,
i.e. the file and the plot. Deriving from gobject, it implement support
for basic arithmetics and support for transactions for recursive updates.

A Signal contains a list of data points, with an identifier, a reference (abscisse) and a string representing the unit of the data.
The Signal contains the ordinate values, while the abscisses are contained
into the Reference Signal.
The identifier is the Signal Name, as presented to the user.

The concept of *transactions* is used to manage Signal dependencies. This is used to make the Signal aware that its data is being to be changed and to notify also its dependent Signals.
Transactions are a way to notify Signals using the current Signal that its data is changing. Once the current Signal has finished its transaction, dependent Signal might recompute their own data.
In this system is defined the 'Dependent' (or 'Lower') Signal, that depends on data from the 'Upper' Signal. For example in v1 = v2 + v3, v1 is the Dependent Signal and v2 and v3 are Upper Signals.
GObject event signaling system is used for the implementation.

Note that pertinent calls to Signal.connect() shall be performed by the user. See examples for arithmetic operations.

Class Signal -- Contains the signal points and other information
   GObject properties (also available as object @property):
       name     read           user-visible identifier
       unit     read           ordinate axis text
       data     read/write     the list of data points
       ref      read/write     Reference Signal. None means this is a Reference.
       freeze   read/write     Disable change Signal data if True
   Other properties
       in_transaction          Non-null when a transaction is ongoing
       to_recompute            True when an Upper Signal data has changed and a
                               recomputation is required
   Signals
       'begin-transaction' is received to notify that Upper Signal data is being
           changed. Event re-emitted toward dependencies
       'changed' is received when Upper Signal data has changed
       'recompute' is emitted once all Upper Signals have finished their
           Transaction
       'end-transaction' is emitted once the Signal data is recomputed to notify
           dependencies that they can recompute their own data
                     
   __init__(name, unit)
      Instanciate an empty signal. If name is a Signal, then return a copy.

   __str__()
      Returns a string with the signal name, the reference name
      and the reader name.
"""
import operator
import numpy
import gobject

# Signals class
class Signal(gobject.GObject):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'recompute': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'begin-transaction': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'end-transaction': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

    __gproperties__ = {
        'ref' : (gobject.TYPE_PYOBJECT,
                 'Reference signal',
                 'Abcisse of the signal',
                 gobject.PARAM_READWRITE),
        'data': (gobject.TYPE_PYOBJECT,
                 'Signal data',
                 'Values of the signals',
                 gobject.PARAM_READWRITE),
        'freeze': (gobject.TYPE_BOOLEAN,
                   'Freeze status',
                   'When True signal updates are disabled',
                   False,
                   gobject.PARAM_READWRITE),
        'name': (gobject.TYPE_STRING,
                 'Signal nickname',
                 'Name displayed to the user',
                 '',
                 gobject.PARAM_READABLE),
        'unit': (gobject.TYPE_STRING,
                 'Signal unit',
                 'Unit in which the data is expressed',
                 '',
                 gobject.PARAM_READABLE)
        }

    __op_name = {
        operator.add: '+',
        operator.sub: '-',
        operator.mul: '*',
        operator.div: '/',
    }

    def __init__(self, value="", unit=""):
        """ Act as a copy constructor if value is a Signal and set the callbacks
        for dependency management. Otherwise act as a usual constructor
        """
        gobject.GObject.__init__(self)
        if isinstance(value, Signal):
            self._data = value._data
            self._name = value._name
            if value.ref is None:
                self._ref = value._ref
            else:
                self._ref = Signal(value._ref)
            self._unit = value._unit if unit == "" else unit
            self._freeze = value.freeze
            self.in_transaction = 0
            self.to_recompute = False
            if self._ref is not None:
                # Not a reference signal
                value.connect('begin-transaction', self.on_begin_transaction)
                value.connect('end-transaction', self.on_end_transaction)
                value.connect('changed', self.on_changed, value)
                self.connect('recompute', self.on_recompute, (None, None, value))
        else:
            self._data = []            # Data points
            self._name = value        # Identifier
            self._ref = None          # Reference signal
            self._unit = unit         # Unit of the signal
            self._freeze = False      # Flag for update
            self.in_transaction = 0
            self.to_recompute = False
            
    def __repr__(self):
        ref_name = self.ref.name if self.ref else '(no reference)'
        if self.data is not None:
            if len(self.data) > 4:
                data = '[%s, %s, ..., %s, %s]' % (self.data[0],
                                                  self.data[1],
                                                  self.data[-2],
                                                  self.data[-1])
            else:
                data = '[' + ', '.join(map(str, self.data)) + ']'
        else:
            data = 'None'
        return '<%s[0x%x] %s / %s [%s] data=%s>' % (type(self).__name__, id(self),
                                                    self.name, ref_name, self.unit,
                                                    data)

    def __iter__(self):
        return iter(self.data)

    def do_set_data(self, data=[]):
        """ Set the data points of the signal
        """
        if data is None:
            self._data = data
            self.emit('changed')
        elif len(data) > 0 :
            if isinstance(data, list):
                self._data = numpy.array(data)
                self.emit('changed')
            elif isinstance(data, numpy.ndarray):
                self._data = data
                self.emit('changed')
            else:
                assert 0, _("Data %s not handled") % type(data)

    def set_data(self, value):
        return self.set_property('data', value)

    def get_data(self):
        """ Return the list of point of the signal
        """
        return self.get_property('data')

    def do_set_ref(self, ref=None):
        """ Set the reference signal
        If set_ to None, then signal is a reference signal (Time, Freq)
        """
        if ref is None or isinstance(ref, Signal):
            self._ref = ref
        else:
            return

    def set_ref(self, value):
        return self.set_property('ref', value)

    def get_ref(self):
        """ Return the reference signal
        """
        return self.get_property('ref')

    @property
    def name(self):
        """ Return the signal name
        """
        return self.get_property('name')

    @property
    def unit(self):
        """ Return the unit of the signal
        """
        return self.get_property('unit')

    def get_freeze(self):
        """ Tell to update or not the signal
        """
        return self.get_property('freeze')

    def set_freeze(self, value):
        """ Tell to update or not the signal
        """
        return self.set_property('freeze', value)

    def do_get_property(self, property):
        """ GObject method
        """
        if property.name == 'ref':
            return self._ref
        elif property.name == 'data':
            return self._data
        elif property.name == 'freeze':
            return self._freeze
        elif property.name == 'name':
            return self._name
        elif property.name == 'unit':
            return self._unit
        else:
            raise AttributeError, _('unknown property %s') % property.name

    def do_set_property(self, property, value):
        """ GObject method
        """
        if property.name == 'ref':
            self.do_set_ref(value)
        elif property.name == 'data':
            self.do_set_data(value)
        elif property.name == 'freeze':
            self._freeze = value
        elif property.name == 'name':
            self._name = value
        elif property.name == 'unit':
            self._unit = value
        else:
            raise AttributeError, _('unknown property %s') % property.name

    ref = property(get_ref, set_ref)
    data = property(get_data, set_data)
    freeze = property(get_freeze, set_freeze)

    def __make_method(op):
        """ Return a function for operator op
        """
        def func(self, other):
            """ Check the operand, perform the operation and set the callbacks
            for dependency management
            """
            other_name = other.name if isinstance(other, Signal) else str(other)
            other_data = other.data if isinstance(other, Signal) else other
            name = '(%s %s %s)' % (self.name, Signal.__op_name[op], other_name)

            s = Signal(name, None)
            s.data = op(self.data, other_data)
            # The new signal has the reference of this signal
            # or this signal if no reference found (e.g. v2=sin(v1.ref))
            s.ref = self.ref if self.ref is not None else self
            s.freeze = self.freeze
            # Handle dependencies
            # Here surely there will have room for memory optimisation
            # as we keep in memory the intermediate signals:
            # v1 = v2 + v3 + v4 becomes v1 = v2 + (v3 + v4) where the
            # operation between parenthesis is an intermediate signal.
            # We store the signal and the operation within the callback
            # arguments
            # Here again this could be optimised by identifying only the
            # subsignals that have changed an running only the pertinent
            # recomputations
            self.connect('changed', s.on_changed, self)
            self.connect('begin-transaction', s.on_begin_transaction)
            self.connect('end-transaction', s.on_end_transaction)
            if isinstance(other, Signal):
                other.connect('changed', s.on_changed, other)
                other.connect('begin-transaction', s.on_begin_transaction)
                other.connect('end-transaction', s.on_end_transaction)
            s.connect('recompute', s.on_recompute, (op, self, other))
            return s
        return func

    def __make_method_inplace(op):
        """ Return a function for operator op, inplace version
        """
        def func(self, other):
            """ Check the operand, perform the operation and set the callbacks
            for dependency management
            """
            other_data = other.data if isinstance(other, Signal) else other
            self.data = op(self.data, other_data)
            if isinstance(other, Signal):
                other.connect('changed', self.on_changed, self)
                other.connect('begin-transaction', self.on_begin_transaction)
                other.connect('end_transaction', self.on_end_transaction)
            return self
        return func

    __add__ = __make_method(operator.add)
    __iadd__ = __make_method_inplace(operator.iadd)

    __sub__ = __make_method(operator.sub)
    __isub__ = __make_method_inplace(operator.isub)

    __mul__ = __make_method(operator.mul)
    __imul__ = __make_method_inplace(operator.imul)

    __div__ = __make_method(operator.div)
    __idiv__ = __make_method_inplace(operator.idiv)

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__

    def __neg__(self):
        name = '-%s' % self.name
        s = Signal(name, None)
        s.data = -self.data
        self.connect('changed', s.on_changed)
        self.connect('begin-transaction', s.on_begin_transaction)
        self.connect('end-transaction', s.on_end_transaction)
        return s

    def on_begin_transaction(self, event, data=None):
        """ Go to transaction, notify Lower Signals that this one might be
        changed
        """
        self.in_transaction = self.in_transaction + 1
        if self.in_transaction < 2:
            # Prevent event being emitted twice
            self.emit('begin-transaction')

    def on_end_transaction(self, event, data=None):
        """ Exit from transaction. Once all Upper Signals have completed their
        transaction, recompute this one and notify Lower Signals
        """
        self.in_transaction = self.in_transaction - 1
        if self.in_transaction == 0:
            # Prevent events being emitted twice
            self.emit('recompute')
            self.emit('end-transaction')

    def on_changed(self, event, data=None):
        """ An Upper Signal changed, this one will have to be recomputed
        """
        self.to_recompute = True
        # Here we might store which Signal changed
        self.emit('changed')
        
    def on_recompute(self, event, args=None):
        """ Call again the function that was used to comoute the data of this
        signal.
        Args shall be a tuple containing:
        op: operator or function to call, None for an assignation (v2 = v1)
        s: first operand
        other: second operand
        out: (optional) output Signal, used for numpy.ufuncs
        """
        if not self.to_recompute or args is None:
            return
        if self.in_transaction > 0:
            return
        if not self.freeze:
            op = args[0]
            if op is None:
                # Operation is a direct assignation (i.e. v2 = v1)
                (op, s, other) = args
                self.data = other.data
            elif len(args) == 3:
                (op, s, other) = args
                # Other operation (+, -, *, /)
                other_data = other.data if isinstance(other, Signal) else other
                s_data = s.data if isinstance(s, Signal) else s
                self.data = op(s_data, other_data)
            elif len(args) == 4:
                (op, s1, s2, out) = args
                s1_data = s1.data if isinstance(s1, Signal) else s1
                s2_data = s2.data if isinstance(s2, Signal) else s2
                self.data = op(s1_data, s2_data, out.data)
            to_recompute = False
