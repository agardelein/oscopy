dist_pkgdata_DATA = ipython_config.py \
	ioscopy.ui \
	new_math_signal_dlg.glade \
	run_netnsim_dlg.glade \
	signal-list.ui

ipython_config.py: ipython_config.py.in
	cat $< | sed -e 's|@bindir[@]|$(bindir)|g' > $@