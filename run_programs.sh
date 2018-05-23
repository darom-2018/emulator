#!/bin/sh

test -n "$srcdir" || srcidr=$(dirname "$0")
test -n "$srcdir" || srcdir=.

programs="$(awk '/\$PROGRAM/{getline; print}' ${srcdir}/storage_devices/test_programs | sed 's/"//g')"

"${srcdir}/emulator.py" --cli --storage-device "${srcdir}/storage_devices/test_programs" $programs;
