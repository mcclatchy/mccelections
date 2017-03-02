#!/bin/bash

if [[ -z $PSQL_CONNECTION ]] ; then
    echo 'Add $PSQL_CONNECTION to bash env vars.'
    exit 1
fi


DIR_PATH=/home/ubuntu/gatest/usable

SLEEP_TIME=60

FILES=$DIR_PATH/*

for file in $FILES
do

    echo "--------------------------------------"
    date "+STARTED: %H:%M:%S"
    echo ""

    ## TRUNCATE
    # echo "Truncating all tables"
    # $PSQL_CONNECTION "TRUNCATE TABLE results_ballotmeasure, results_candidate, results_datasource, results_election, results_location, results_officename, results_race, results_race_candidate_mm,results_reportingunit, results_result, results_resultlive, results_resultmanual, results_resultstage, results_seatname, results_storylink CASCADE;"
    
    echo ""

    ## virtualenv and cd
    # echo "Activating virtualenv and cd'ing into directory"
    # workon mccelections && cd ~/mccelections/electionsproject
    # echo ""
    ## load
    echo "Loading ${file}"
    # python manage.py loaddata $file ## this doesn't work, gah!
    echo ""

    date "+ENDED: %H:%M:%S"
    echo "--------------------------------------"
    echo ""

    ## sleep
    echo "Sleeping for ${SLEEP_TIME}"
    sleep $SLEEP_TIME
done    
