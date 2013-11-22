#!/bin/sh
#-*-Shell-*-

IPYTHON=ipython3
IOSCOPY=ioscopy
PYTHON=python3
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
print("\n" + ip.profile_dir.location + "\n")
EOF`;
    rm $tmpf
}

$IPYTHON profile list --log-level=40 | grep $IOSCOPY > /dev/null
if [ $? -ne 0 ]; then
    echo IPython $IOSCOPY profile not found, creating it.
    $IPYTHON profile create $IOSCOPY
    getprofd
    if [ ! -d $profd  ]; then
	mkdir -p $profd
    fi
    if [ a$profd = a ]; then
	echo Profile directory not found.
	exit
    fi
    cp @datarootdir@/oscopy/ipython_config.py $profd
    if [ $? -ne 0 ]; then
	echo Unable to copy profile, see message above
	exit
    fi
else
    getprofd
    if [ a$profd = a ]; then
	echo Profile directory not found.
	exit
    fi
    if [ ! -f "$profd/ipython_config.py" ]; then
	echo IPython $IOSCOPY profile file not found, copying it.
	cp @datarootdir@/oscopy/ipython_config.py $profd
	if [ $? -ne 0 ]; then
	    echo Unable to copy profile, see message above
	    exit
	fi
    elif [ "$profd/ipython_config.py" -ot "@datarootdir@/oscopy/ipython_config.py" ]; then
	echo
	upd=0
	read -p "IPython $IOSCOPY profile file is outdated, update [N/y] ? " upd
	echo
	if [ "$upd" = "Y" -o "$upd" = "y" ] ; then
	    echo Updating IPython $IOSCOPY profile.
	    echo
	    cp @datarootdir@/oscopy/ipython_config.py $profd
	    if [ $? -ne 0 ]; then
		echo Unable to copy profile, see message above
		exit
	    fi
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
