#!/bin/bash

if [[ -z $PSQL_CONNECTION ]] ; then
    echo 'Add $PSQL_CONNECTION to bash env vars.'
    exit 1
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
    echo "Missing value for AP_TEST. Execute 'export AP_TEST=True' or 'export AP_TEST=False'"
    exit 1
fi

if [[ -z $SAVER_PATH ]] ; then
    echo "Missing SAVER_PATH. Add 'export SAVER_PATH=/path/to/dir' to .bashrc." # originally said bash_profile
    exit 1
fi


## defining commands

ELEX_COMMAND="elex results $RACE_DATE"

COPY_COMMAND_RESULTSTAGE="COPY results_resultstage FROM stdin DELIMITER ',' CSV HEADER;"

TRUNCATE_COMMAND_RESULTSTAGE="TRUNCATE TABLE results_resultstage CASCADE;"

mkdir -p ${SAVER_PATH}/tmp

touch ${SAVER_PATH}/tmp/results.csv

# chmod u+x ${SAVER_PATH}/tmp/results.csv

FILE=${SAVER_PATH}/tmp/results.csv


## DOWNLOAD data

echo ""
echo "------------------------------"
date "+STARTED: %H:%M:%S"

start_time=$(date +%s)
echo ""

## check if a test and download
if [ $AP_TEST = True ]; 
    then        
        echo "Downloading test data for $RACE_DATE"
        $ELEX_COMMAND -t > $FILE
    else
        echo "Downloading non-test data for $RACE_DATE"
        $ELEX_COMMAND > $FILE
fi

end_time=$(date +%s)
diff=$((end_time-start_time))

echo ""
echo "$((diff / 60)) minutes and $((diff % 60)) seconds"
echo ""

date "+ENDED: %H:%M:%S"
echo "------------------------------"
echo ""

## LOAD data

echo "------------------------------"
date "+STARTED: %H:%M:%S"

start_time=$(date +%s)
echo ""

## truncate table
$PSQL_CONNECTION "${TRUNCATE_COMMAND_RESULTSTAGE}"
echo ""

## load data
$PSQL_CONNECTION "COPY results_resultstage FROM STDIN DELIMITER ',' CSV HEADER;" < "${FILE}"
echo "Data loaded for ${RACE_DATE}"

end_time=$(date +%s)
diff=$((end_time-start_time))

echo ""
echo "$((diff / 60)) minutes and $((diff % 60)) seconds"
echo ""

date "+ENDED: %H:%M:%S"
echo "------------------------------"
echo ""
echo ""


