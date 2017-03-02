echo "Running psql command to TRUNCATE TABLE for ResultStage"
$PSQL_CONNECTION "TRUNCATE TABLE results_resultstage CASCADE;"