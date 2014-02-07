dist_pkgdata_DATA = ipython_config.py \
	ioscopy.ui

ipython_config.py: ipython_config.py.in
	cat $< | sed -e 's|@bindir[@]|$(bindir)|g' > $@