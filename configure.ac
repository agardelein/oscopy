dnl                                                      -*-Autoconf-*-
dnl Process this file with autoconf to generate configure.
dnl
dnl The AX_* macros are defined in files in the top-level m4
dnl directory.

#####################################################################
# Set up configuration system
#####################################################################

AC_INIT([oscopy], [0.70.0-rc1], [agardelein@yahoo.fr])
AC_CONFIG_AUX_DIR([build-tools])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

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
AM_PATH_PYTHON([2.5])

#####################################################################
# Check for libraries that use pkg-config
#####################################################################

PKG_PROG_PKG_CONFIG

PKG_CHECK_MODULES(PYGTK, [pygtk-2.0 >= 2.10.0], ,
  AC_MSG_ERROR([PyGTK 2.10.0 or later is required.]))

###################################
### Internationalization
###################################
GETTEXT_PACKAGE=oscopy
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.41.0])

AC_OUTPUT
