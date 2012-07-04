mysubdirs = scheme po src

if CAN_BUILD_DOC
SUBDIRS = $(mysubdirs) doc
else
SUBDIRS = $(mysubdirs)
endif

oscopydir = $(pkgpythondir)

dist_doc_DATA = README

dist_datadir = $(datarootdir)/oscopy

dist_pkgdata_DATA = ipython_config.py

docdir = $(datarootdir)/doc/oscopy

ACLOCAL_AMFLAGS = -I m4

bin_SCRIPTS = ioscopy

ioscopy: ioscopy_app.sh
	cat $< | sed -e 's|@datarootdir[@]|$(datarootdir)|g' > $@
	chmod u+x $@

ipython_config.py: data/ipython_config.py
	cat $< | sed -e 's|@bindir[@]|$(bindir)|g' > $@