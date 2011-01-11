#!/usr/bin/python
#-*-Shell-*-
#if [[ ! -e ${HOME}/.ipython/ipythonrc-oscopy ]]; then
#    cp @datarootdir@/oscopy/ipythonrc-oscopy ${HOME}/.ipython
#fi
#ipython -pylab -profile oscopy -noconfirm_exit -nobanner

import gtk, gobject, sys, os, shutil
import IPython.Shell
live = False

try:
    os.stat(os.getenv('HOME') + '/.ipython/ipythonrc-oscopy')
except OSError, e:
    shutil.copy2('@datarootdir@/oscopy/ipythonrc-oscopy', os.getenv('HOME') + '/.ipython')

def run_ipython():
    global live
    if live:
        return False

    live = True
    shell = IPython.Shell.IPShellMatplotlib(argv=['-pylab','-profile','oscopy','-noconfirm_exit','-nobanner'])
    IPython.Shell.hijack_gtk()
    shell.mainloop()
    gtk.main_quit()
    sys.exit()

gobject.idle_add(run_ipython)
gtk.set_interactive(True)
gtk.main()
