""" Export signals to Gnucap format

class GnucapWriter -- Handle gnucap format

   get_fmt_name()
   Return 'gnucap'

   fmt_check()
   Return True if all signals have the same reference

   write_sigs()
   Write the signals to file

   format_sig_name()
   Convert signal name to gnucap format e.g. vgs -> v(gs)
"""

from Writer import Writer

class GnucapWriter(Writer, object):
    """ Write signals to columns tab separated format used by Gnucap
    Signals should have the same reference
    """
    def get_fmt_name(self):
        """ Return the format name
        """
        return 'gnucap'

    def fmt_check(self, sigs):
        """ Check if all signals have the same reference
        """
        if not sigs:
            return False
        elif len(sigs) > 1:
            # More than one signal, compare reference signals
            prevs = None
            for s in sigs.itervalues():
                if prevs is None:
                    # First iteration
                    prevs = s
                else:
                    # Ugly but == on array returns an array of bool
                    # how to find a False into this ?
                    for a, b in zip(s.get_ref().get_data(), \
                                        prevs.get_ref().get_data()):
                        if a == b:
                            continue
                        else:
                            return False
            return True
        else:
            # Only one signal, do not need to compare the reference
            return True

    def write_sigs(self, sigs):
        """ Write signals to file
        Loop through all the data of each signal to write
        columns line by line.

        Gnucap format is (tab separated):
        Time|Freq v(x) v(y) v(aa) ...
        1.234   1.234   1.234  1.234
        1.234   1.234   1.234  1.234
        1.234   1.234   1.234  1.234
        ...

        A for loop is build to have the following string, (then run by exec()):
        _f.write("#" + "Time" + _sep + "v(x)" + _sep + ...)
        for Time, x, y, z, ... in zip(sigs["x"].get_ref().get_data(), \
                           sigs['x'].get_data(), \
                           sigs['y'].get_data(), \
                           sigs['z'].get_data(), \
                           ...
                           ):
            _f.write(Time + _sep + x + _sep + y + _sep + z ...)
        h contains the header writing line
        f contains the for variable names
        z contains the zip variables
        d contains the data writing line
        """
        _sep = "\t"
#        print "Writing gnucap file"
        # Overwrite file or not
        self.ow = True
        if self.ow:
            mode = "w"
        else:
            mode = "a"
#        print self.fn
        _f = open(self.fn, mode)
        if _f is None:
            print "Oops"
            return
        first = 0
        for sn, s in sigs.iteritems():
            if not first:
                first = 1
                # Variable names, beginning of for
                f = "for %s, %s" % (s.get_ref().get_name(), sn)
                # Zip part
                z = "in zip(sigs[\"%s\"].get_ref().get_data()" % sn
                z += ", sigs[\"%s\"].get_data()" % sn
                # Header
                h = "_f.write(\"#\" + \"%s\" + _sep + \"%s\"" % \
                    (self.format_sig_name(s.get_ref().get_name()), \
                    self.format_sig_name(s.get_name()))
                # Data line, float conversion to get 1.234 instead of 1,234
                d = "\t_f.write(str(float(%s)) + _sep + str(float(%s))" % \
                    (s.get_ref().get_name(), sn)
            else:
                f += ", %s" % sn 
                z += ", sigs[\"%s\"].get_data()" % sn
                h += " + _sep + \"%s\"" % self.format_sig_name(s.get_name())
                # Float conversion to get_ 1.234 instead of 1,234
                d += " + _sep + str(float(%s))" % sn
        h += " + \"\\n\")\n"
        f += " "
        z += "):\n"
        d += "+\"\\n\")\n"
        _expr = h + f + z + d
#        print _expr
        del h, f, z, d, first, mode
        exec(_expr)
        _f.close()
        return

    def format_sig_name(self, sn):
        """ Add parenthesis in the signal name to be compatible
        with gnucap format
        """
        l = ['v', 'vout', 'vin', 'i', 'p', 'nv', 'ev', 'r', 'y',\
                 'z', 'zraw', 'pd', 'ps', 'f', 'input', 'ioffset_',\
                 'ipassive', 'pi', 'pidb', 'pm', 'pmdb', 'pp']
        l.sort()
        l.reverse()
        for n in l:
            if sn.startswith(n):
                return n + '(' + sn.replace(n, '', 1) + ')'
                break
        return sn
