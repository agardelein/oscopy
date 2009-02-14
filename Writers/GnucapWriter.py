""" Export signals to Gnucap format

class GnucapWriter -- Handle gnucap format

   getfmtname()
   Return 'gnucap'

   fmtcheck()
   Return True if all signals have the same reference

   writesigs()
   Write the signals to file

   addpar()
   Convert signal name to gnucap format e.g. vgs -> v(gs)
"""

import Writers.Writer

class GnucapWriter(Writers.Writer.Writer):
    """ Write signals to columns tab separated format used by Gnucap
    Signals should have the same reference
    """
    def getfmtname(self):
        """ Return the format name
        """
        return 'gnucap'

    def fmtcheck(self, sigs):
        """ Check if all signals have the same reference
        """
        if len(sigs) < 1:
            return False
        elif len(sigs) > 1:
            prevs = None
            for s in sigs.itervalues():
                if prevs == None:
                    # First iteration
                    prevs = s
                else:
                    # Ugly but == on array returns an array of bool
                    # how to find a False into this ?
                    for a, b in zip(s.getref().getpts(), \
                                        prevs.getref().getpts()):
                        if a == b:
                            continue
                        else:
                            return False
            return True
        else:
            return True

    def writesigs(self, sigs):
        """ Write signals to file
        """
        _sep = "\t"
#        print "Writing gnucap file"
        # Overwrite file or not
        self.ow = True
        if self.ow == True:
            mode = "w"
        else:
            mode = "a"
#        print self.fn
        _f = open(self.fn, mode)
        if _f == None:
            print "Oops"
            return
        first = 0
        for sn, s in sigs.iteritems():
            if not first:
                first = 1
                # Variable names, beginning of for
                f = "for "
                f = f + s.getref().getname() + ","
                f = f + sn
                # Zip part
                z = "in zip(sigs[\"" + sn + "\"].getref().getpts()"
                z = z + ", sigs[\"" + sn + "\"].getpts()"
                # Header
                h = "_f.write(\"#\" + \"" \
                    + self.addpar(s.getref().getname()) + "\""
                h = h + " + _sep + \"" + self.addpar(s.getname()) + "\""
                # Data line, float conversion to get 1.234 instead of 1,234
                d = "\t_f.write(str(float(" + s.getref().getname() + "))"
                d = d + " + _sep + str(float(" + sn + "))"
            else:
                f = f + "," + sn 
                z = z + ", sigs[\"" + sn + "\"].getpts()"
                h = h + " + _sep + \"" + self.addpar(s.getname()) + "\""
                # Float conversion to get 1.234 instead of 1,234
                d = d + " + _sep + str(float(" + sn + "))"
        h = h + " + \"\\n\")\n"
        f = f + " "
        z = z + "):\n"
        d = d + "+\"\\n\")\n"
        _expr = h + f + z + d
#        print _expr
        del h, f, z, d, first, mode
        exec(_expr)
        _f.close()
        return

    def addpar(self, sn):
        """ Add parenthesis to the signal name to be compatible
        with gnucap format
        """
        l = ['v', 'vout', 'vin', 'i', 'p', 'nv', 'ev', 'r', 'y',\
                 'z', 'zraw', 'pd', 'ps', 'f', 'input', 'ioffset',\
                 'ipassive', 'pi', 'pidb', 'pm', 'pmdb', 'pp']
        l.sort()
        l.reverse()
        for n in l:
            if sn.startswith(n):
                return n + '(' + sn.replace(n, '', 1) + ')'
                break
        return sn
