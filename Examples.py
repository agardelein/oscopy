from pylab import *
import matplotlib.pyplot as plt
import pygtk
pygtk.require('2.0')
import gtk

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

def myplot():
    t = arange(0.0, 2.0, 0.01)
    s = sin(2*pi*t)
    xscale('log')
    plot(t, s*s, linewidth=1.0)
    
    xlabel('time (s)')
    ylabel('voltage (mV)')
    title('About as simple as it gets, guys')
    grid(True)
    show()

def myline():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Click to build line segments')
    line, = ax.plot([0],[0])
    linebuilder = LineBuilder(line)
    plt.show()

def hi():
    print __name__
    if __name__ == "Examples":
        hello = HelloWorld()
        hello.main()
