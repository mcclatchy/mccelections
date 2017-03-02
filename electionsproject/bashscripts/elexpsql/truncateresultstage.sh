#!/bin/bash

if [[ -z $PSQL_CONNECTION ]] ; then
    echo 'Add $PSQL_CONNECTION to bash env vars.'
    exit 1
fi


## defining commands

TRUNCATE_COMMAND_RESULTSTAGE="TRUNCATE TABLE results_resultstage CASCADE;"

# TRUNCATE_COMMAND_RESULTSTAGEMIRROR="TRUNCATE TABLE results_resultstagemirror CASCADE;"

## truncating tables

echo ""
echo "CLEARNING EVERYTHING OUT TO START"
echo ""

# TRUNCATE resultstage tabble
echo "Running psql command to TRUNCATE TABLE for ResultStage for $RACE_DATE"
$PSQL_CONNECTION "${TRUNCATE_COMMAND_RESULTSTAGE}"
echo ""


# # TRUNCATE resultstagemirror tabble
# echo "Running psql command to TRUNCATE TABLE for ResultStageMirror for $RACE_DATE"
# $PSQL_CONNECTION "${TRUNCATE_COMMAND_RESULTSTAGEMIRROR}"
# echo ""



