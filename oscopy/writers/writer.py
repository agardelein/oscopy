""" Common signal export functions
"""

import os.path

class WriteError(Exception):
    """
Class WriteError -- Errors encountered when writing file
methods:
    __init__(value)
      Assign the error message

    __str__()
      Return a string with the error message
    """
    def __init__(self, msg):
        """ Assign the error message

        Parameter
        ---------
        msg: string
        The error message

        Returns
        -------
        WriteError
        The object instanciated
        """
        self._msg = msg

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
        return self._msg

class Writer(object):
    """ Writer -- Provide common function for exporting signals into files
The purpose of this class is to provide some basic functions to write the
Signals to files (file validation) thus simplifying the definition of
Writers for many different file formats.

The derived classes must redefine _get_format_name, _format_check and
write_signals.
    """
    def __init__(self):
        """ Instanciate the Reader

        Parameter
        ---------
        None

        Returns
        -------
        Writer
        The object instanciated
        """
        self._fn = ""
        self._ow = False   # Overwrite flag
        self._opts = {}    # Options passed to write()

    def write(self, fn, sigs, opts = {}):
        """ Do some checks before calling write_signals

        Parameters
        ----------
        fn: string
        Path to the output file

        sigs: dict of Signals
        List of Signals to write in the file

        opts: dict of various data with strings as keys
        Options to be considered for the writing

        Returns
        -------
        bool
        True if operation completed successfully

        Raises
        ------
        WriteError
        In case of invalid path or invalid file format
        """
        if isinstance(opts, dict):
            self._opts = opts
        # Overwrite option
        if self._opts.has_key("ow"):
            if self._opts["ow"] in ['True', 'true', '1']:
                self._ow = True
            else:
                self._ow = False
        if self._check(fn) and self._format_check(sigs):
            return self.write_signals(sigs)
        else:
            return False

    def _check(self, fn):
        """ Common checks on file access

        Parameter
        ---------
        fn: string
        Path to the file to validate

        Returns
        -------
        Nothing

        Raises
        ------
        WriteError
        In case no file is specified, file exist and overwrite is not allowed
        or file access issue
        """
        if not (isinstance(fn, str) or isinstance(fn, unicode)):
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

    def _format_check(self, sigs):
        """ Format specific checks, to be overridden by derived classes

        Parameter
        ---------
        sigs: dict of Signals
        The Signal list to write

        Returns
        -------
        bool
        True if no issue found to write the Signal list in this format
        """
        return False

    def _get_format_name(self):
        """ Return the format name

        Parameter
        ---------
        None

        Returns
        -------
        string
        The format identifier
        """
        return None

    def detect(self, format):
        """ Return True if format format is supported

        Parameter
        ---------
        format: string
        Identifier of the whised format

        Returns
        -------
        bool
        True if this Writer manage this format
        """
        if (isinstance(format, str) or isinstance(format, unicode))\
                and format == self._get_format_name():
            return True
        else:
            return False

    def write_signals(self, sigs):
        """ Write Signals to file
        This function must be redefined in the derived class
        
        Parameter
        ---------
        sigs: dict of Signals
        The list of Signals to write

        Returns
        -------
        Nothing
        """
        return
