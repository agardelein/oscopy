#! /bin/sh

autoreconf -i \
&& automake --add-missing \
&& autoconf

