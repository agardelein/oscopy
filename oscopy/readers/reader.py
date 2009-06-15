""" Common file read functions

Class ReadError -- Errors encountered when loading file
   methods:
   __init__(value)
      Assign the error message

   __str__()
      Return a string with the error message

Class Reader -- Define the common functions for reader objects

   methods:
   read(fi)
      Check if the file can be opened before calling _read_signals(),

   _read_signals()
      To be defined into the derived objects
      Read the signals from the file, fill slist
      and return a dict of the signals, with the signame as key.

   update()
      Reread the file and return a dict of the reread signals,
      toget_her with a list of the updated, deleted and added signals

   detect(fn)
      Return  if the object recognize the file

   _check(fn)
      Raise ReadError exception if file fn is not accessible

   __str__()
      Return the filename

"""

import os.path

class ReadError(Exception):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self._value

class Reader(object):
    """ Reader -- Provide common function for signal file reading
    The derived class must redefine _read_signals() and detect()
    """
    def __init__(self):
        self._fn = ""
        self._signals = {}
        self._update_num = -1  # Update number

    # Certify the path is valid and is a file
    def read(self, fn):
        """ Check if the path is a valid file and call _read_signals
        """
        self._check(fn)
        self._fn = fn
        return self._read_signals()

    def _read_signals(self):
        """ Read the signal list from the file, fill self.slist
        and return a dict of the signals, with the signal name as a key
        """
        return {}

    # Re-read the data file
    # Return signal list and names of updated, deleted and new signals
    def update(self, upn, keep=True):
        """ On new update requests (upn > self._update_num), reread the file
        and update self._signals.
        Update signals, but if unit or reference is not found,
        mark signal as being deleted if keep is False (see below)
        If _read_signals returns nothing (file is deleted or whatever), all
        signals are considered deleted
        If signal is not found or either reference or unit changed, de
        If keep is False, the signal is marked as being deleted, i.e. its
        data set to None
        Return dict of new signals
        """
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
        for sn, s in oldsigs.iteritems():
            if sn not in sigs:
                if not keep:
                    s.data = None
 #                   print s.name, "DELETED !"
        self._update_num = upn
        self._signals = oldsigs
        return n

    def detect(self, fn):
        """ Check if the file provided can be read by this object
        """
        return False

    def _check(self, fn):
        """ Check if the file is accessible
        Raise ReadError exception if not accessible
        """
        if not fn:
            raise ReadError("No file specified")
        if not os.path.exists(fn):
            raise ReadError("File do not exist")
        if not os.path.isfile(fn):
            raise ReadError("File is not a file")

    def __str__(self):
        """ Return the signal name.
        """
        return self._fn

    @property
    def signals(self):
        """ Return the list of signals names
        """
        return self._signals
