SUBDIRS = oscopy scheme

oscopydir = $(pkgpythondir)

dist_doc_DATA = README

dist_datadir = $(datarootdir)/oscopy

dist_pkgdata_DATA = ipythonrc-oscopy

ACLOCAL_AMFLAGS = -I m4

bin_SCRIPTS = oscopy_app

oscopy_app: ioscopy_app.py
	cat ioscopy_app.py | sed -e 's|@datarootdir[@]|$(datarootdir)|g' > oscopy_app
	chmod u+x oscopy_app