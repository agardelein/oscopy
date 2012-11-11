""" Common file read functions
"""

import os.path
import time
import gobject
from oscopy import Signal

class ReadError(Exception):
    """
Class ReadError -- Errors encountered when loading file
methods:
    __init__(value)
      Assign the error message

    __str__()
      Return a string with the error message

    """
    def __init__(self, value):
        """ Assign the error message

        Parameter
        ---------
        Value: string
        The error message

        Returns
        -------
        ReaderError
        The object instanciated
        """
        self._value = value

    def __str__(self):
        """ Returns the error message

        Parameter
        ---------
        None

        Returns
        -------
        string
        The error message
        """
        return self._value

class Reader(gobject.GObject):
    """ Reader -- Provide common function for Signal files reading
Derives from GObject.GObject
The purpose of this class is to provide some basic functions to read the Signals
from files (file validation, update process) thus simplifying the definition of
Readers for many different file formats.
The derived class must redefine _read_signals() and detect().

Properties
    signals     The list of Signal handled by the class
    info        Various informations on the reader (last time read...)

Signals
    begin-transation    File is being re-read from disk and Signals updated
    end-transaction     Operation completed, Signals updated
    """
    __gsignals__ = {
        'begin-transaction': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'end-transaction': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

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
        gobject.GObject.__init__(self)
        self._fn = ""          # file name
        self._signals = {}     # Internal Signal list
        self._update_num = -1  # Update number
        self._info = {}        # Misc information (e.g. last update timestamp)
        self._renamed = {}     # Translation of renamed signals

    def read(self, fn):
        """ Validate the file and read the Signals from the file.
        This function call _check() and _read_signals().

        Parameter
        ---------
        fn: string
        The filename

        Returns
        -------
        Dict of Signals
        The list of Signals read from the file

        Raises
        ------
        ReaderError
        In case of invalid path or unsupported file format
        """
        self._check(fn)
        self._fn = fn
        self._info['file'] = self._fn
        self._info['last_update'] = time.time()
        for s in self._read_signals().itervalues():
            self.connect('begin-transaction', s.on_begin_transaction)
            self.connect('end-transaction', s.on_end_transaction)
        return self._signals

    def _read_signals(self):
        """ Read the signal list from the file, fill self.slist
        and return a dict of the signals, with the signal name as a key
        When this function is called self._fn is already initialized with the
        filename and the filename is valid.

        Parameter
        ---------
        None

        Returns
        -------
        Dict of Signals
        The list of Signals read from the file
        """
        return {}

    # Re-read the data file
    # Return signal list and names of updated, deleted and new signals
    def update(self, upn, keep=True):
        """ On new update requests, reread the file and update self._signals.
        Existing Signals are marked as being deleted if 'keep' is False
        and either:
           * Signal not found
           * Unit or reference of the Signal is not found
           * Unit or reference of the Signal has changed
           * _read_signals returns an empty dictionnary
        
        Parameters
        ----------
        upn: integer
        Update request identifier. If upn > self._update_num then this is a new
        request.

        keep: bool
        When True Signals marked as being deleted are removed from the interal
        Signal list

        Returns
        -------
        n: dict of Signals
        The list of new Signals
        """
        # FIXME: Hmmm... it seems the temporary signals are not deleted, i.e.
        # the ones that are reread but already existing.
        if upn <= self._update_num:
            # Already updated
            return {}

        # Save the old list and reread the file
        oldsigs = self._signals
        sigs = self._read_signals()
        # Update the old signal dict with new one
        # Find the new signals, update signals not frozen, mark deleted signals
        # and for updated signals check whether ref, ref unit or unit
        # has changed
        n = {}
        for sn, s in sigs.iteritems():
            if sn not in oldsigs:
                # New signal
                n[sn] = s
                oldsigs[sn] = s
 #               print "New signal:", sn
            else:
                if oldsigs[sn].freeze:
                    # Signal is frozen, no update
 #                   print sn, "is frozen"
                    continue
                os = oldsigs[sn]
                ns = sigs[sn]
                if os.unit == ns.unit and \
                        os.ref.unit == ns.ref.unit and \
                        os.ref.name == ns.ref.name:
                    # Unit, reference unit and reference name are the same so
                    # Update !
                    os.ref.data = ns.ref.data
                    os.data = ns.data
 #                   print os.name, "updated !"
                else:
                    # Something changed, do not update
                    if not keep:
                        os.data = None
 #                   print os.name, "not updated: something changed"

        # Find deleted signals, i.e. present in old dict but not in new one
        d = []
        for sn, s in oldsigs.iteritems():
            if sn not in sigs:
                if not keep:
                    s.data = None
                    d.append(sn)
 #                   print s.name, "DELETED !"
        self._update_num = upn
        self._signals = oldsigs
        # Delete signals from dict
        for sn in d:
            del self._signals[sn]
        self._info['last_update'] = time.time()
        return n

    def detect(self, fn):
        """ Check if the file provided can be read by this object
        This function shall be redefined in derived class

        Parameter
        ---------
        fn: string
        Path to the file to test

        Returns
        -------
        bool
        True if the file can be handled by this reader
        """
        return False

    def _check(self, fn):
        """ Check if the file is accessible
        Raise ReadError exception if not accessible

        Parameter
        ---------
        fn: string
        Path to the file to validate

        Returns
        -------
        Nothing

        Raises
        ------
        ReadError
        In case the path does not exist or is not a regular file
        """
        if not fn:
            raise ReadError(_("No file specified"))
        if not os.path.exists(fn):
            raise ReadError(_("File do not exist"))
        if not os.path.isfile(fn):
            raise ReadError(_("File is not a file"))

    def __str__(self):
        """ Return the path to the file.

        Parameter
        ---------
        None

        Returns
        -------
        string
        The path to the file
        """
        return self._fn

    @property
    def signals(self):
        """ Return the list of Signals

        Parameter
        ---------
        None

        Returns
        -------
        dict of Signals
        The list of Signals
        """
        return self._signals

    @property
    def info(self):
        """ Return the reader infos

        Parameter
        ---------
        None

        Returns
        -------
        dict of various data where keys are strings
        Information on file (e.g. last update timestamp)
        """
        return self._info

    def on_begin_transaction(self, event):
        """ Go to transaction, notify Listener Signals that this Reader might be
        changed
        Event is emitted only once, at first notification.

        Parameters
        ----------
        event: Not used
        data: Not used

        Returns
        -------
        Nothing
        """
        self.in_transaction = True
        self.emit('begin-transaction')

    def on_end_transaction(self, event):
        """ Exit from transaction and notify Listener Signals.
        Event is emitted only once, at last notification and after data
        recomputation.

        Parameters
        ----------
        event: Not used
        data: Not used

        Returns
        -------
        Nothing
        """
        self.in_transaction = False
        self.emit('end-transaction')

    def rename_signal(self, oldname, newname):
        if oldname not in self._signals.keys():
            return

        self._renamed[oldname] = newname
        
        os = self._signals[oldname]
        ns = Signal(newname, os.unit)
        ns.ref = os.ref
        ns.data = os.data
        ns.freeze = os.freeze

        del self._signals[oldname]
        self._signals[newname] = ns
        return ns
