""" Common signal export functions

class Writer -- Define the common functions for writing files

   methods:
   write()
   Do some checks and call write_sigs

   write_sigs()
   Write signals to files

   _check()
   Mainly check if file is writable

   _fmt_check()
   Called for format specific check

   _get_fmt_name()
   Return a string containing format name

   detect()
   Return true if format is supported
"""

import os.path
import numpy

class WriteError(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

class Writer(object):
    """ Writer -- Provide common function for exporting signals into files
    The derived classes must redefine _get_fmt_name and write_sigs.
    """
    def __init__(self):
        self._fn = ""
        self._ow = False   # Overwrite flag
        self._opts = {}    # Options passed to write()

    def write(self, fn, sigs, opts = {}):
        """ Do some checks before calling write_sigs
        """
        if isinstance(opts, dict):
            self._opts = opts
        # Overwrite option
        if self._opts.has_key("ow"):
            if self._opts["ow"] in ['True', 'true', '1']:
                self._ow = True
            else:
                self._ow = False
        if self._check(fn) and self._fmt_check(sigs):
            return self.write_sigs(sigs)
        else:
            return False

    def _check(self, fn):
        """ Common checks on file access
        """
        if not isinstance(fn, str):
            raise WriteError("No string specified")
        if not fn:
            raise WriteError("No file specified")
        if os.path.exists(fn):
            if not self._ow:
                self._fn = fn
                raise WriteError("File already exist")
            elif not os.path.isfile(fn):
                raise WriteError("File exists but is not a file")
            elif not os.access(fn, os.W_OK):
                raise WriteError("Cannot access file")
        elif not os.access(os.path.dirname(fn), os.W_OK):
            raise WriteError("Cannot access destination directory")
        self._fn = fn
        return True

    def _fmt_check(self, sigs):
        """ Format specific checks, to be overridden by derived classes
        """
        return False

    def _get_fmt_name(self):
        """ Return the format name
        """
        return None

    def detect(self, fmt):
        """ Return True if format fmt is supported
        """
        if isinstance(fmt, str) and fmt == self._get_fmt_name():
            return True
        else:
            return False

