#!/bin/sh

test -n "$srcdir" || srcidr=$(dirname "$0")
test -n "$srcdir" || srcdir=.

set -e

programs="$(awk '/\$PROGRAM/{getline; print}' ${srcdir}/storage_devices/test_programs | sed 's/"//g')"

for program in $programs; do
    "${srcdir}/emulator.py" --cli --storage-device "${srcdir}/storage_devices/test_programs" "$program" --input 5;
done
