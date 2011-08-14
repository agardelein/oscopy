#!/usr/bin/python2
#-*-Shell-*-
#if [[ ! -e ${HOME}/.ipython/ipythonrc-oscopy ]]; then
#    cp @datarootdir@/oscopy/ipythonrc-oscopy ${HOME}/.ipython
#fi
#ipython -pylab -profile oscopy -noconfirm_exit -nobanner

GETTEXT_DOMAIN = 'oscopy'
import gettext

import gtk, gobject, sys, os, shutil
import IPython.Shell
live = False

gettext.install(GETTEXT_DOMAIN,'@datarootdir@/locale',unicode=1)

try:
    os.stat(os.getenv('HOME') + '/.ipython/ipythonrc-oscopy')
except OSError, e:
    os.symlink('@datarootdir@/oscopy/ipythonrc-oscopy', os.getenv('HOME') + '/.ipython/ipythonrc-oscopy')

def run_ipython():
    global live
    if live:
        return False

    live = True
    shell = IPython.Shell.IPShell(argv=['-profile','oscopy','-noconfirm_exit','-nobanner'])
    IPython.Shell.hijack_gtk()
    shell.mainloop()
    gtk.main_quit()
    sys.exit()

gobject.idle_add(run_ipython)
gtk.set_interactive(True)
gtk.main()
