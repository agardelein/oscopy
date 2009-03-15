""" Commandline application using Cmd
"""

import re
#from Oscopy.Cmd import Cmds
from Cmd import Cmd


class Oscopy:
    """ Analyse command arguments and call function from Cmd
    See Cmd for more help
    """
    def __init__(self):
        self.cmds = Cmd()

    def create(self, args):
        if args == "help":
            print "Usage : create [SIG [, SIG [, SIG]...]]"
            print "   Create a new figure, set_ it as current, add the signals"
            return
        self.cmds.create(self.get_toplot(args))

    def destroy(self, args):
        if args == "help":
            print "Usage : delete FIG#"
            print "   Delete a figure"
            return        
        self.cmds.destroy(eval(args))

    def select(self, args):
        if args == "help":
            print "Usage: select FIG#[, GRAPH#]"
            print "   Select the current figure and the current graph"
            return
        s = args.split('-')
        num = eval(s[0])
        if len(s) > 1:
            gn = eval(s[1])
        else:
            gn = 0
        self.cmds.select(num, gn)

    def layout(self, args):
        if args == "help":
            print "Usage : layout horiz|vert|quad"
            print "   Define the layout of the current figure"
            return
        self.cmds.layout(args)

    def figlist(self, args):
        if args == "help":
            print "Usage : figlist"
            print "   Print the list of figures"
            return
        self.cmds.figlist()

    def plot(self, args):
        if args == "help":
            print "Usage : plot"
            print "   Draw and show the figures"
            return
        self.cmds.plot()

    def read(self, args):
        if args == "help":
            print "Usage : load DATAFILE"
            print "   Load signal file"
            return
        fn = args
        return self.cmds.read(fn)

    def write(self, args):
        if args == "help":
            print "Usage: write format [(OPTIONS)] FILE SIG [, SIG [, SIG]...]"
            print "   Write signals to file"
            return
        # Extract format, options and signal list
        tmp = re.search(r'(?P<fmt>\w+)\s*(?P<opts>\([^\)]*\))?\s+(?P<fn>[\w\./]+)\s+(?P<sigs>\w+(\s*,\s*\w+)*)', args)

        if tmp == None:
            print "What format ? Where ? Which signals ?"
            return
        fmt = tmp.group('fmt')
        fn = tmp.group('fn')
        opt = tmp.group('opts')
        sns = self.get_toplot(tmp.group('sigs'))
        opts = {}
        if opt != None:
            for on in opt.strip('()').split(','):
                tmp = on.split(':', 1)
                if len(tmp) == 2:
                    opts[tmp[0]] = tmp[1]
        self.cmds.write(fn, fmt, sns, opts)

    def update(self, args):
        if args == "help":
            print "Usage: update"
            print "   Reread data files"
            return
        self.cmds.update()

    def add(self, args):
        if args == "help":
            print "Usage : add SIG [, SIG [, SIG]...]"
            print "   Add a graph to the current figure"
            return
        self.cmds.add(self.get_toplot(args))

    def delete(self, args):
        if args == "help":
            print "Usage : delete GRAPH#"
            print "   Delete a graph from the current figure"
            return
        self.cmds.delete(args)

    def mode(self, args):
        if args == "help":
            print "Usage: mode MODE"
            print "   Set the type of the current graph of the current figure"
            print "Available modes :\n\
   lin      Linear graph\n\
   fft      Fast Fourier Transform (FFT) of signals\n\
   ifft     Inverse FFT of signals"
            return
        self.cmds.mode(args)

    def scale(self, args):
        if args == "help":
            print "Usage: scale [lin|logx|logy|loglog]"
            print "   Set the axis scale"
            return
        self.cmds.scale(args)

    def range(self, args):
        if args == "help":
            print "Usage: range [x|y min max]|[xmin xmax ymin ymax]|[reset_]"
            print "   Set the axis range of the current graph of the current figure"
            return
        tmp = args.split()
        if len(tmp) == 1:
            if tmp[0] == "reset_":
                self.cmds.range(tmp[0])
        elif len(tmp) == 3:
            if tmp[0] == 'x' or tmp[0] == 'y':
                self.cmds.range(tmp[0], float(tmp[1]), float(tmp[2]))
        elif len(tmp) == 4:
            self.cmds.range(float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3]))

    def unit(self, args):
        if args == "help":
            print "Usage: unit [XUNIT,] YUNIT"
            print "   Set the unit to be displayed on graph axis"
            return

        us = args.split(",", 1)
        if len(us) < 1:
            return
        elif len(us) == 1:
            self.cmds.unit(us[0].strip())
        elif len(us) == 2:
            self.cmds.unit(us[0].strip(), us[1].strip())
        else:
            return

    def insert(self, args):
        if args == "help":
            print "Usage: insert SIG [, SIG [, SIG]...]"
            print "   Insert a list of signals into the current graph"
            return
        self.cmds.insert(self.get_toplot(args))

    def remove(self, args):
        if args == "help":
            print "Usage: remove SIG [, SIG [, SIG]...]"
            print "   Delete a list of signals into from current graph"
            return
        self.cmds.remove(self.get_toplot(args))

    def freeze(self, args):
        if args == "help":
            print "Usage: freeze SIG [, SIG [, SIG]...]"
            print "   Do not consider signal for subsequent updates"
        self.cmds.freeze(self.get_toplot(args))

    def unfreeze(self, args):
        if args == "help":
            print "Usage: unfreeze SIG [, SIG [, SIG]...]"
            print "   Consider signal for subsequent updates"
        self.cmds.unfreeze(self.get_toplot(args))

    def siglist(self, args):
        if args == "help":
            print "Usage : siglist"
            print "   List loaded signals"
            return
        self.cmds.siglist()

    def math(self, inp):
        if inp == "help":
            print "Usage: destsig=mathexpr"
            print "   Define a new signal destsig using mathematical expression"
            return
        self.cmds.math(inp)

    def get_toplot(self, args):
        sns = []
        if args == "":
            sns = []
        else:
            for sn in args.split(","):
                sns.append(sn.strip())
        return sns

    def help(self, args):
        """ Display help messages
        """
        if args == "":
            print "\
Commands related to figures:\n\
   create      create a new figure\n\
   destroy     delete a figure\n\
   select      define the current figure and the current graph\n\
   layout      set_ the layout (either horiz, vert or quad)\n\
   figlist     list the existing figures\n\
   plot        draw and show the figures\n\
Commands related to graphs:\n\
   add         add a graph to the current figure\n\
   delete      delete a graph from the current figure\n\
   mode        set_ the mode of the current graph of the current figure\n\
   unit        set_ the units of the current graph of the current figure\n\
   scale       set_ the scale of the current graph of the current figure\n\
   range       set_ the axis range of the current graph of the current figure\n\
Commands related to signals:\n\
   read        read signals from file\n\
   write       write signals to file\n\
   update      reread signals from file(s)\n\
   insert      add a signal to the current graph of the current figure\n\
   remove      delete a signal from the current graph of the current figure\n\
   (un)freeze  toggle signal update\n\
   siglist     list the signals\n\
Misc commands:\n\
   echo        print a message\n\
   pause       wait for the user to press enter\n\
   quit, exit  exit the program\n\
   help        display this help message\n\
\n\
During plot:\n\
   1, 2        Toggle first and second vertical cursors\n\
   3, 4        Toggle first and second horizontal cursors\n\
\n\
Help for individual command can be obtained with 'help COMMAND'\
"
        else:
            if args in dir(cmds):
                eval("self." + args + "(\"help\")")
            else:
                print "Unknown command", args

    def echo(self, args):
        if args == "help":
            print "Usage: echo [TEXT]"
            print "   Print text"
            return
        print args        

    def pause(self, args):
        if args == "help":
            print "Usage: pause"
            print "   Wait for the user to press enter"
            return
        inp = raw_input("Press enter")
