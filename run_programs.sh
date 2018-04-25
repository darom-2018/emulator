#!/bin/sh

# Remove once test_ini runs under CLI
# set -e

test -n "$srcdir" || srcidr=$(dirname "$0")
test -n "$srcdir" || srcdir=.

for program in `find "${srcdir}/programs" -type f`; do
    "${srcdir}/emulator.py" --cli "$program";
done
