#!/bin/sh
#-*-Shell-*-

IPYTHON=ipython
IOSCOPY=ioscopy
PYTHON=python
IOCFG=--IOscopyConfig
REPS="'-b': '$IOCFG.b=True $IOCFG.f=',\
'-i': '$IOCFG.i=True',\
'-h': '$IOCFG.h=True',\
'-H': '-h',\
'-q': '--no-banner --IOscopyConfig.quiet=True'"

getprofd () {
    tmpf=tmpfile
    profd=`$IPYTHON --quick --profile=$IOSCOPY --no-banner --quiet --no-confirm-exit --classic --HistoryManager.hist_file=$tmpf<< EOF| grep /
ip=get_ipython()
print "\n" + ip.profile_dir.location + "\n"
EOF`;
    rm $tmpf
}

# Is IPython there ?
which $IPYTHON > /dev/null
if [ $? -ne 0 ]; then
    echo IPython not found
    exit
fi

# Validate version of IPython. Option name changed between 0.10 and 0.13.
if [ `$IPYTHON --version | tr -d . | cut -c 1-3` -lt "013" ]; then
    echo IPython > 0.13 needed to run IOscopy
    exit
elif [ `$IPYTHON --version | tr -d . | cut -c 1-3` -lt "013" ]; then
    echo IPython > 0.13 needed to run IOscopy
    exit
fi

# Now IPython version is validated, let's look for ioscopy profile
$IPYTHON profile list --log-level=40 | grep $IOSCOPY > /dev/null
if [ $? -ne 0 ]; then
    echo IPython $IOSCOPY profile not found, creating it.
    $IPYTHON profile create $IOSCOPY
    getprofd
    if [ ! -d $profd  ]; then
	mkdir -p $profd
    fi
    cp @datarootdir@/oscopy/ipython_config.py $profd
else
    getprofd
    if [ ! -f "$profd/ipython_config.py" ]; then
	echo IPython $IOSCOPY profile file not found, copying it.
	cp @datarootdir@/oscopy/ipython_config.py $profd
    elif [ "$profd/ipython_config.py" -ot "@datarootdir@/oscopy/ipython_config.py" ]; then
	echo
	upd=0
	read -p "IPython $IOSCOPY profile file is outdated, update [N/y] ? " upd
	echo
	if [ "$upd" = "Y" -o "$upd" = "y" ] ; then
	    echo Updating IPython $IOSCOPY profile.
	    echo
	    cp @datarootdir@/oscopy/ipython_config.py $profd
	else
	    echo "skipping profile update."
	    echo
	fi
    fi
fi

# Replace short args with their equivalent, and delete space between = and
# file name when needed
args=`$PYTHON <<EOF
reps={$REPS}
argout=[reps.get(s, s) for s in "$*".split()]
print " ".join(argout).replace(".f= ", ".f=")
EOF`
#echo ///// $args +++++++++++++++++++++++
$IPYTHON --profile=$IOSCOPY $args
