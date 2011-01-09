#!/bin/sh
#-*-Shell-*-
if [[ ! -e ${HOME}/.ipython/ipythonrc-oscopy ]]; then
    cp @datarootdir@/oscopy/ipythonrc-oscopy ${HOME}/.ipython
fi
ipython -pylab -profile oscopy -noconfirm_exit -nobanner
