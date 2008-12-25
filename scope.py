#!/usr/bin/python
# Hello world
import readline

from Examples import *
from Cmd import *

# Readline configuration
hist_file = ".scope_history"
readline.read_history_file(hist_file)

# Prompt
p = "scope> "
cmds = Cmds()

# Main loop
while True:
    try:
        inp = raw_input(p)
        # Check if command is assignment
        if inp.find("=") >= 0:
            cmds.math(inp)
            continue

        # Separate command from args
        if inp.find(" ") >= 0:
            st = inp.split(' ', 1)    
            cmd = st[0]
            args = st[1]
        else:
            cmd = inp
            args = ""
            
        # End of program
        if cmd == "exit" or cmd == "quit":
            break

        # Evaluate the command
        eval("cmds." + cmd + "(args)")
        continue

    except EOFError:
        break

    except AttributeError, e:
        print "Unknown command:", e.message
        continue

    except NameError, e:
        print "Unknown command", e.message
        continue

    except SyntaxError, e:
        print "Syntax Error", e.message
        continue

    except LoadFileError, e:
        print "Error in loadfile :", e.value

readline.write_history_file(hist_file)

