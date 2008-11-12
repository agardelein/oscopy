#!/usr/bin/python
# Hello world
import readline

from Examples import *
from Cmd import *

def byebye():
    readline.write_history_file(hist_file)
    exit

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
            load(args)
            continue
                
        if cmd == "hi":
            hi()
                
        if cmd == "plot":
            myplot()
            continue

        if cmd == "line":
            myline()
            continue
            
    except EOFError:
        break

    except LoadFileError, e:
        print "Error in loadfile :", e.value

byebye()

