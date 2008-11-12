#!/usr/bin/python
# Hello world
from __future__ import with_statement
import readline
import pygtk
pygtk.require('2.0')
import gtk
from pylab import *
import matplotlib.pyplot as plt

# Signals class
class Signal:
    name = ""     # Identifier for cmdline
    origfile = "" # Comes from
    origname = "" # Name as it appear in the file
    domain = ""   # Domain, time for now...

# Get signals from line
def getsiglist(names, file):
    slist = []
    nlist = names.split()
    domain = nlist.pop(0)
    for name in nlist:
        s = Signal()
        s.domain = domain
        s.origfile = file
        # Original signal name
        s.origname = name ;
        # Signal name
        s.name = ""
        for i in name.strip():
            if i!='(' and i!= ')': s.name = s.name + i
        slist.append(s)
    return slist
        
# Read the variable list from file
def loadfile(file):
    if args == "":
        print "load: no file specified"
        return False
    with open(file) as f:
        s = f.readline()
    s = s.lstrip('#')
    return getsiglist(s, file)

def byebye():
    readline.write_history_file(hist_file)
    exit

class HelloWorld:
    def hello(self, widget, data=None):
        print "Hello World"

    def delete_event(self, widget, event, data=None):
        print "delete event occurred"
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        self.window.set_border_width(10)
        self.button = gtk.Button("Hello World")
        self.button.connect("clicked", self.hello, None)

        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
        self.window.add(self.button)
        self.button.show()
        self.window.show()

    def main(self):
        gtk.main()

class LineBuilder:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print 'click', event
        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()

class MyMotion:
    def __init__(self):
        

# Readline configuration
hist_file = ".scope_history"
readline.read_history_file(hist_file)

str = "Hello World !"
print str
slist = [] ;
# Prompt
p = "scope> "

# Main loop
while True:
    try:
        inp = raw_input(p)
        # Separate command from args
        if inp.find(" ") >= 0:
            st = inp.split(' ', 1)    
            cmd = st[0]
            args = st[1]
        else:
            cmd = inp
            args = ""
            
        # Dispatch command
        if cmd == "exit" or cmd == "quit":
            break
        if cmd == "load":
            slist = loadfile(args)
            print args, ":"
            for ns in slist:
                print ns.name, "/", ns.domain
        if cmd == "hi":
            print __name__
            if __name__ == "__main__":
                hello = HelloWorld()
                hello.main()
        if cmd == "plot":
            t = arange(0.0, 2.0, 0.01)
            s = sin(2*pi*t)
            xscale('log')
            plot(t, s*s, linewidth=1.0)

            xlabel('time (s)')
            ylabel('voltage (mV)')
            title('About as simple as it gets, guys')
            grid(True)
            show()

        if cmd == "line":
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_title('Click to build line segments')
            line, = ax.plot([0],[0])
            linebuilder = LineBuilder(line)
            plt.show()

        if cmd == "mot":
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_title('Plouf plouf')
            

    except EOFError:
        break

byebye()

