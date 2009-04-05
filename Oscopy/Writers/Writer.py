""" Common signal export functions

class Writer -- Define the common functions for writing files

   methods:
   write()
   Do some checks and call writesigs

   writesigs()
   Write signals to files

   check()
   Mainly check if file is writable

   fmtcheck()
   Called for format specific check

   get_fmtname()
   Return a string containing format name

   detect()
   Return true if format is supported
"""

import os.path
import numpy

class WriteError:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class Writer:
    """ Writer -- Provide common function for exporting signals into files
    The derived classes must redefine get_fmtname and writesigs.
    """
    def __init__(self):
        self.fn = ""
        self.ow = False   # Overwrite flag
        self.opts = {}    # Options passed to write()

    def write(self, fn, sigs, opts = {}):
        """ Do some checks before calling writesigs
        """
        if isinstance(opts, dict):
            self.opts = opts
        # Overwrite option
        if self.opts.has_key("ow"):
            if self.opts["ow"] in ['True', 'true', '1']:
                self.ow = True
            else:
                self.ow = False
        if self.check(fn) and self.fmtcheck(sigs):
            return self.writesigs(sigs)
        else:
            return False

    def check(self, fn):
        """ Common checks on file access
        """
        if not isinstance(fn, str):
            raise WriteError("No string specified")
        if fn == "":
            raise WriteError("No file specified")
        if os.path.exists(fn):
            if self.ow == False:
                self.fn = fn
                raise WriteError("File already exist")
            elif not os.path.isfile(fn):
                raise WriteError("File exists but is not a file")
            elif not os.access(fn, os.W_OK):
                raise WriteError("Cannot access file")
        elif not os.access(os.path.dirname(fn), os.W_OK):
            raise WriteError("Cannot access destination directory")
        self.fn = fn
        return True

    def fmtcheck(self, sigs):
        """ Format specific checks, to be overridden by derived classes
        """
        return False

    def get_fmtname(self):
        """ Return the format name
        """
        return None

    def detect(self, fmt):
        """ Return True if format fmt is supported
        """
        if isinstance(fmt, str) and fmt == self.get_fmtname():
            return True
        else:
            return False

