""" Handle signals created by the user


"""

import time

from reader import Reader, ReadError
from oscopy import Signal

class SignalReader(Reader):
    def __init__(self):
        self._sig = None
        self._name = ""
        Reader.__init__(self)
        pass

    def read(self, args):
        """ Do not check for filename validity, and signal name is a composition
        of the name of the signal and its expression
        """
        (self._sig, self._name) = args
        self._fn = "%s=%s" % (self._name, self._sig.name)
        self._info['file'] = self._fn
        self._info['last_update'] = time.time()
        sigs = self._read_signals()
        for s in sigs.itervalues():
            self._sig.connect('changed', s.on_changed)
            s.connect('recompute', s.on_recompute, (None, s, self._sig))
            self._sig.connect('begin-transaction', s.on_begin_transaction)
            self._sig.connect('end-transaction', s.on_end_transaction)
        return sigs

    def _read_signals(self):
        sig = Signal(self._name, self._sig.unit)
        sig.data = self._sig.data
        sig.freeze = self._sig.freeze
        sig.ref = self._sig.ref
        self._signals = {self._name: sig}
        self.connect('begin-transaction', self._sig.on_begin_transaction)
        self.connect('end-transaction', self._sig.on_end_transaction)
        return self._signals
 
    def detect(self, name):
        return True if isinstance(name, Signal) else False
