#!/usr/bin/python
"""
Sample command line application
"""
import oscopy
from optparse import OptionParser


if __name__ == "__main__":
    # Parse command line arguments
    # Current options:
    #   -b : batch mode, read commands from file
    #   -i : interactive mode, do not quit at the end of batch file
    #   -q : do not display startup message
    parser = OptionParser()
    parser.add_option("-b", "--batch", dest="fn",\
                          help="Execute commands in FILE then exit",\
                          metavar="FILE")
    parser.add_option("-i", "--interactive", action="store_true",\
                          dest="inter",\
                          help="Go to interactive mode after executing batch file")
    parser.add_option("-q", "--quiet", action="store_true",\
                          dest="quiet",\
                          help="Do not display startup message")
    (options, args) = parser.parse_args()

    o = oscopy.OscopyApp()
    # do_Exec(filename)
    if options.fn is not None:
        o.do_exec(options.fn)
        if options.inter:
            if options.quiet:
                o.cmdloop("")
            else:
                o.cmdloop()
    else:
        if options.quiet:
            o.cmdloop("")
        else:
            o.cmdloop()
                
