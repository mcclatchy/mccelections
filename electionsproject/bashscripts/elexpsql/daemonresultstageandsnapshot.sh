#!/bin/sh

# ./truncateresultstage.sh

while [ 1 ]; do
	./loadresultsstage.sh
	# ./snapshot.sh ## keep commented out until snapshot saves to different location (i.e. S3 instead of the same server it runs on)
    sleep 60
done
