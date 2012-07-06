#!/bin/sh
#-*-Shell-*-

IPYTHON=ipython
IOSCOPY=ioscopy

getprofd () {
    profd=`$IPYTHON --quick --profile=$IOSCOPY --no-banner --quiet --no-confirm-exit --classic<< EOF| grep /
ip=get_ipython()
print "\n" + ip.profile_dir.location + "\n"
EOF`;
}

$IPYTHON profile list --log-level=40 | grep $IOSCOPY > /dev/null
if [ $? -ne 0 ]; then
    echo IPython $IOSCOPY profile not found, creating it.
    $IPYTHON profile create $IOSCOPY
    getprofd
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
args=$*
args=`echo $* | sed -e 's/-b[[:space:]]*/--IOscopy.batch=True --IOscopy.file=/; s/-i/--IOscopy.interactive=True/ ; s/-h/--IOscopy.help=True/ ; s/-H/-h/; s/-q/--IOscopy.quiet=True/'`
$IPYTHON --profile=$IOSCOPY $args
