dnl                                                      -*-Autoconf-*-
dnl Process this file with autoconf to generate configure.
dnl
dnl The AX_* macros are defined in files in the top-level m4
dnl directory.

#####################################################################
# Set up configuration system
#####################################################################

AC_INIT([oscopy], [0.72-rc1], [arnaud@oscopy.org])
AC_CONFIG_AUX_DIR([build-tools])
AM_INIT_AUTOMAKE([-Wall foreign])

AC_PROG_LN_S
AC_CONFIG_MACRO_DIR([m4])

AC_ARG_WITH([doc],
	[AC_HELP_STRING([--with-doc],
			 [build documentation (LaTeX and graphviz required)])],
			 [with_doc=yes],
			 [with_doc=no])
AC_SUBST(with_doc)

can_build_documentation=$with_doc

AC_CONFIG_FILES([
	Makefile
	src/oscopy_ipython/Makefile
	src/oscopy_ipython/gui/Makefile
	src/Makefile
	src/oscopy/Makefile
	src/oscopy/graphs/Makefile
	src/oscopy/readers/Makefile
	src/oscopy/writers/Makefile
	scheme/Makefile
	doc/Makefile
	doc/ioscopy/Makefile
	doc/ioscopy/tex/Makefile
	doc/ioscopy/pdf/Makefile
	doc/oscopy-api/Makefile
	doc/oscopy-api/tex/Makefile
	doc/oscopy-api/pdf/Makefile
	po/Makefile.in
	data/Makefile
])

#####################################################################
# Check whether documentation can be build
#####################################################################
AC_MSG_CHECKING([whether documentation shall be built])
AM_CONDITIONAL([CAN_BUILD_DOC], [test x$with_doc = xyes])
AC_MSG_RESULT($can_build_documentation)
AC_SUBST(can_build_documentation)

#####################################################################
# Check for compiling & linking tools
#####################################################################

AC_PATH_PROGS([M4], [gm4 m4], [m4])
AM_PATH_PYTHON([3.4])

AM_PATH_IPYTHON3([2.3])
AM_CHECK_MATPLOTLIB([1.4])
AM_CHECK_NUMPY([1.6])
AM_CHECK_DBUS_PYTHON([1.1])
#####################################################################
# Check for libraries that use pkg-config
#####################################################################

PKG_PROG_PKG_CONFIG

PKG_CHECK_MODULES(Cairo, [cairo >= 1.12], ,
  AC_MSG_ERROR([Cairo 1.12 or later is required.]))
PKG_CHECK_MODULES(PyGObject, [pygobject-3.0 >= 3.14], ,
  AC_MSG_ERROR([PyGObject 3.14 or later is required.]))

###################################
### Internationalization
###################################
GETTEXT_PACKAGE=oscopy
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.41.0])

AC_OUTPUT
