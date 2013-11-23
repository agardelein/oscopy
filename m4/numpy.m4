## numpy.m4 - Check for numpy version on a system. -*-Autoconf-*-
## Copyright (C) 2013 Arnaud Gardelein.
## Author: Arnaud Gardelein <arnaud@oscopy.org>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## As a special exception to the GNU General Public License, if you
## distribute this file as part of a program that contains a
## configuration script generated by Autoconf, you may include it under
## the same distribution terms that you use for the rest of that program.

# AM_PATH_NUMPY([MINIMUM-VERSION], [ACTION-IF-FOUND], [ACTION-IF-NOT-FOUND])
# ---------------------------------------------------------------------------
# Adds support for distributing Numpy modules and packages.
# Call AM_PATH_IPYTHON before using it
#
# If the MINIMUM-VERSION argument is passed, AM_PATH_NUMPY will
# cause an error if the version of IPYTHON installed on the system
# doesn't meet the requirement.  MINIMUM-VERSION should consist of
# numbers and dots only.

AC_DEFUN([AM_CHECK_NUMPY],
 [
  AC_CACHE_CHECK([for Numpy version], [am_cv_numpy_version],
    [am_cv_numpy_version=`$IPYTHON3 --colors=NoColor -c "import numpy,sys; sys.stdout.write(numpy.version.version)"`])
  AC_SUBST([NUMPY_VERSION], [$am_cv_numpy_version])
  AM_NUMPY_CHECK_VERSION([$IPYTHON3], [$1], [$2], [m4_default([$3], [AC_MSG_ERROR([Numpy version > $1 needed])])])
])

# AM_NUMPY_CHECK_VERSION(PROG, VERSION, [ACTION-IF-TRUE], [ACTION-IF-FALSE])
# ---------------------------------------------------------------------------
# Run ACTION-IF-TRUE if the IPYTHON interpreter PROG has version >= VERSION.
# Run ACTION-IF-FALSE otherwise.

AC_DEFUN([AM_NUMPY_CHECK_VERSION],
 [prog="import sys, numpy;minver = list(map(int, '$2'.split('.'))) + [[0, 0, 0]];ver = list(map(int, numpy.version.version[[0:3]].split('.'))) + [[0, 0, 0]];minverhex = sum([[minver[i]<<((4-i)*8) for i in range(0, 4)]]);verhex = sum([[ver[i]<<((4-i)*8) for i in range(0, 4)]]);sys.stdout.write('1' if verhex < minverhex else '0');"
  AS_IF([AM_RUN_LOG_IPYTHON3([$1 --colors=NoColor -c "$prog"])], [$3], [$4])])

