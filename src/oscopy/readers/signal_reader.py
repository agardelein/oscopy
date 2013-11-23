import time

from .reader import Reader, ReadError
from oscopy import Signal

class SignalReader(Reader):
    """ Handle one Signal created by the user.
    This is used when a Signal is imported inside a Context.
    
    Redefines also __init__() and read() from Reader as no file I/O are
    performed and only one Signal is managed.
    """

    def __init__(self):
        """ Instanciate the Reader

        Parameter
        ---------
        None

        Returns
        -------
        Reader
        The object instanciated
        """
        self._sig = None
        self._name = ""
        Reader.__init__(self)
        pass

    def read(self, args):
        """ Create a Signal from one provided in the argument.
        Do not check for Signal validity, and Signal name is a composition
        of the name of the Signal and its computation expression.
        Set the relevant event connections between the original Signal,
        this Reader and the new Signal.

        Parameter
        ---------
        args: tuple
           Signal: the original Signal
           name: the name of the new Signal

        Returns
        -------
        Dict of one Signal
        The list of one Signal created from the original one
        """
        (self._sig, self._name) = args
        self._fn = "%s=%s" % (self._name, self._sig.name)
        self._info['file'] = self._fn
        self._info['last_update'] = time.time()
        sigs = self._read_signals()
        for s in sigs.values():
            self._sig.connect('changed', s.on_changed, self._sig)
            s.connect('recompute', s.on_recompute, (None, s, self._sig))
            self.connect('begin-transaction', s.on_begin_transaction)
            self.connect('end-transaction', s.on_end_transaction)
        return sigs

    def _read_signals(self):
        """ Instanciated the Signal from the original one, 
        and return a dict of one Signal, with the Signal name as a key
        When this function is called self._fn is already initialized with the
        filename.

        Parameter
        ---------
        None

        Returns
        -------
        Dict of one Signal
        The list of the Signal generated from the original Signal.
        """
        if self._signals:
            return self._signals
        sig = Signal(self._name, self._sig.unit)
        sig.data = self._sig.data
        sig.freeze = self._sig.freeze
        sig.ref = self._sig.ref
        self._signals = {self._name: sig}
        self._sig.connect('begin-transaction', self.on_begin_transaction)
        self._sig.connect('end-transaction', self.on_end_transaction)
        return self._signals
 
    def detect(self, name):
        """ Check if the Signal provided can be read by this object

        Parameter
        ---------
        name: Signal
        Signal to test

        Returns
        -------
        bool
        True if the Signal can be handled by this reader
        """
        return True if isinstance(name, Signal) else False
