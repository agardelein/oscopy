pkglib_LTLIBRARIES = v_oscopy.la
v_oscopy_la_SOURCES = v_oscopy.c

v_oscopy_la_CFLAGS = $(GCC_CFLAGS) $(GLIB_CFLAGS) $(GTK_CFLAGS)\
	 $(DBUS_CFLAGS)

v_oscopy_la_LDFLAGS = -module
v_oscopy_la_LIBADD = $(DBUS_LIBS)

install-exec-hook:
	cd $(DESTDIR)$(libdir) && \
	$(LN_S) -f @PACKAGE@/v_@PACKAGE@.so v_@PACKAGE@.so

uninstall-hook:
	rm -f $(DESTDIR)$(libdir)/v_@PACKAGE@.so
