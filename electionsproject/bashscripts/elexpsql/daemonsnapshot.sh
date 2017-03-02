#!/bin/sh

# add a counter for 120 (???) times to run if 1/minute snapshots

while [ 1 ]; do
	./snapshot.sh
    sleep 60
done
