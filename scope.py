#!/usr/bin/python
# Hello world
from __future__ import with_statement
import readline

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

    except EOFError:
        break

byebye()

