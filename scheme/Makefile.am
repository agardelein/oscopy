scmdatadir = $(prefix)/share/gEDA/scheme
scmdata_DATA = oscopy.scm
oscopy.scm: oscopy.scm.in
	sed -e "s;@BINDIR@;${bindir};g" \
	    -e "s;@PYEXECDIR@;${pyexecdir};g" $< > $@

all: oscopy.scm

EXTRA_DIST = $(scmdata_DATA)

