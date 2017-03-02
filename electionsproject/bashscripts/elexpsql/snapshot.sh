#!/bin/bash

## environment checks

# set RACE_DATE from the first argument, if it exists
if [[ ! -z $1 ]] ; then
    RACE_DATE=$1
fi

if [[ -z $RACE_DATE ]] ; then
    echo 'Provide a race date, such as export RACE_DATE=2016-02-01.'
    exit 1
fi

if [[ -z $AP_API_KEY ]] ; then
    echo "Missing environmental variable AP_API_KEY. Try 'export AP_API_KEY=MY_API_KEY_GOES_HERE' or add to .bashrc." # originally said bash_profile
    exit 1
fi

if [[ -z $AP_TEST ]] ; then
    echo "Missing value for AP_TEST. Execute 'export AP_TEST=True' or 'export AP_TEST=False' or add to .bashrc." # originally said bash_profile
    exit 1
fi

if [[ -z $SAVER_PATH ]] ; then
    echo "Missing value for SAVER_DIR. Execute 'export AP_TEST=True' or 'export AP_TEST=False' or add to .bashrc." # originally said bash_profile
    exit 1
fi

## commands

# abstract SAVER_DIR with something like modified version of this
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# CURRENT_DIR=
# PARENT_DIR=
# SNAPSHOT_DIR=

# construct path for dir (move to bashrc so it can be used both here and in loadsavedresults.sh?)
FULL_SAVER_PATH=$SAVER_PATH/$RACE_DATE
# construct save date for subdir
SAVE_DATE=$(date +"%Y-%m-%d")
FULL_FILE_PATH=$FULL_SAVER_PATH/$SAVE_DATE

# -p option creates the directory for that date if need
echo ""
mkdir -p $FULL_SAVER_PATH/$SAVE_DATE/
echo "If needed, making new $SAVE_DATE directory for $RACE_DATE election"
echo ""

# for datetime stamp
now=$(date +"%Y-%m-%d_%H-%M-%S")

echo "------------------------------"
date "+STARTED: %H:%M:%S"
echo ""

echo "Snapshotting $RACE_DATE results..."
echo ""

start_time=$(date +%s)

if [[ $AP_TEST = False ]] ; 
	then
		# CSV for non-tests
		echo "Snapshotting elex for non-test results as csv"
		elex results \'$RACE_DATE\' > $FULL_FILE_PATH/results${now}.csv # -t ## why was this here?!
		echo ""
    else
    	# CSV for tests
		echo "Snapshotting elex for test results as csv"
		elex results \'$RACE_DATE\' -t > $FULL_FILE_PATH/results${now}.csv
		echo ""

fi

end_time=$(date +%s)
diff=$((end_time-start_time))

echo "$((diff / 60)) minutes and $((diff % 60)) seconds"


date "+ENDED: %H:%M:%S"
echo "------------------------------"
echo ""
