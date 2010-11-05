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
        self._sig = args[0]
        self._name = args[1]
        self._fn = "%s=%s" % (self._name, self._sig.name)
        self._info['file'] = self._fn
        self._info['last_update'] = time.time()
        return self._read_signals()

    def _read_signals(self):
        self._signals = {self._name: self._sig}
        return self._signals
        pass

    def detect(self, name):
        return True if isinstance(name, Signal) else False
