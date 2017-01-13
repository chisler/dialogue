#!/bin/bash -e

BASEDIR=`dirname $0`/..

if [ ! -d "$BASEDIR/ve" ]; then
    pip install virtualenv
    virtualenv -p /usr/bin/python3.5 $BASEDIR/env
    echo "Virtualenv created."
fi

if [ ! -f "$BASEDIR/env/updated" -o $BASEDIR/dialogue/requirements.txt -nt $BASEDIR/env/updated ]; then
    source $BASEDIR/env/bin/activate
    pip install -r $BASEDIR/dialogue/requirements.txt
    echo "Requirements installed."
fi