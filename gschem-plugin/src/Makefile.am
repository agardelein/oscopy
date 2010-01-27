pkglib_LTLIBRARIES = v_oscopy.la
v_oscopy_la_SOURCES = v_oscopy.c

v_oscopy_la_CFLAGS = $(GCC_CFLAGS) $(GLIB_CFLAGS) $(GTK_CFLAGS)\
	 $(DBUS_GLIB_CFLAGS)

v_oscopy_la_LDFLAGS = -module

install-exec-hook:
	cd $(DESTDIR)$(libdir) && \
	$(LN_S) @PACKAGE@/@PACKAGE@.so .