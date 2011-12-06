#!/bin/sh
#-*-Shell-*-

IPYTHON=ipython
IOSCOPY=ioscopy

$IPYTHON profile list --log-level=40 | grep $IOSCOPY > /dev/null

if [ $? -ne 0 ]; then
    echo IPython $IOSCOPY profile not found, creating it...
    $IPYTHON profile create $IOSCOPY
    profd=`$IPYTHON --profile=ioscopy  --no-banner --quiet --no-confirm-exit --classic<< EOF| grep /
ip=get_ipython()
print "\n" + ip.profile_dir.location + "\n"
EOF`
    echo $profd
    cp @datarootdir@/oscopy/ipython_config.py $profd
fi
$IPYTHON --profile=$IOSCOPY --no-banner --automagic
