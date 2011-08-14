mysubdirs = oscopy scheme po

if CAN_BUILD_DOC
SUBDIRS = $(mysubdirs) doc
else
SUBDIRS = $(mysubdirs)
endif

oscopydir = $(pkgpythondir)

dist_doc_DATA = README

dist_datadir = $(datarootdir)/oscopy

dist_pkgdata_DATA = ipythonrc-oscopy

docdir = $(datarootdir)/doc/oscopy

ACLOCAL_AMFLAGS = -I m4

bin_SCRIPTS = ioscopy

ioscopy: ioscopy_app.py
	cat ioscopy_app.py | sed -e 's|@datarootdir[@]|$(datarootdir)|g' > ioscopy
	chmod u+x ioscopy
