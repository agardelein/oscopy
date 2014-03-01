SUBDIRS=gui

ioscopydir = $(pkgpythondir)/../oscopy_ipython

ioscopy_PYTHON = ioscopyapp.py \
	__init__.py

bin_SCRIPTS = ioscopy.py

ioscopy.py: ioscopy.py.in
	cat $< | sed -e 's|@datarootdir[@]|$(datarootdir)|g' > $@
