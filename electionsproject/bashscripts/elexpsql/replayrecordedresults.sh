#!/bin/bash

if [[ -z $PSQL_CONNECTION ]] ; then
    echo 'Add $PSQL_CONNECTION to bash env vars.'
    exit 1
fi

if [[ -z $REPLAY_RACE_DATE ]] ; then
    echo 'Provide a race date, such as export REPLAY_RACE_DATE=2016-02-01.'
    exit 1
fi

if [[ -z $SAVER_PATH ]] ; then
    echo 'Provide a saver path, such as export SAVER_PATH=/home/ubuntu/mccelections/electionsproject/snapshots/.'
    exit 1
fi

if [[ -z $SAVE_DATE ]] ; then
    echo 'Provide a save date, such as export SAVE_DATE=2016-02-11.'
    exit 1
fi

if [[ -z $SLEEP_TIME ]] ; then
    echo 'Provide a sleep time, such as export SLEEP_TIME=60.'
    exit 1
fi

# construct path for dir (move to bashrc so it can be used both here and in loadsavedresults.sh?)
SAVER_FULL_PATH=$SAVER_PATH/$REPLAY_RACE_DATE

# FULL_FILE_PATH=$SAVER_DIR/$REPLAY_RACE_DATE/$SAVE_DATE

## don't include trailing slash! -- including in FILES below
DIR_PATH=$SAVER_FULL_PATH/$SAVE_DATE

FILES=$DIR_PATH/*

for file in $FILES
do
    echo "--------------------------------------"
    date "+STARTED: %H:%M:%S"
    echo ""

    ## delete results script
    echo "Running psql command to TRUNCATE TABLE for ResultStage for $REPLAY_RACE_DATE"
    ## local
    # psql electionresults -c "TRUNCATE TABLE results_resultstage CASCADE;"
    ## server
    $PSQL_CONNECTION "TRUNCATE TABLE results_resultstage CASCADE;"

    echo "Running psql command to LOAD RESULTS for ${file}"
    # filestring=\'$file\'

    ## local
    # psql electionresults -c "COPY results_resultstage FROM $filestring DELIMITER ',' CSV HEADER;"
    ## prod server
    $PSQL_CONNECTION "COPY results_resultstage FROM STDIN DELIMITER ',' CSV HEADER;" < "${file}"
    echo ""

    date "+ENDED: %H:%M:%S"
    echo "--------------------------------------"
    echo ""

    echo "Sleeping for $SLEEP_TIME"
    sleep $SLEEP_TIME
done
