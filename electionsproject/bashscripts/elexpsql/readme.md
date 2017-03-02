# Set environment variables

Execute `vim ~/.bashrc` in your terminal and paste the following (updating the variables as needed):

	````
	# for all envs
	export AP_API_KEY=<YOUR_AP_API_KEY>
	export AP_TEST=False

	# for mccelections
	# local
	export SAVER_PATH=/<YOUR>/<PATH>/mccelections/electionsproject/snapshots

	# server
	# export SAVER_PATH=/home/ubuntu/mccelections/electionsproject/snapshots
	```

We're not using these for now because this should be done off-server

	export ELEX_RECORDING=flat
	export ELEX_RECORDING_DIR=/tmp/ap-elex-data/

# Prep for live or test election loading or recording

For all .sh files, change permissions
	
	chmod u+x <filename>

To set values for race date

	export RACE_DATE=2016-02-01

and then test status

	export AP_TEST=False

or 

	export AP_TEST=True

## Loading for live or test election 

Then execute for one time

	./loadresultstage.sh

or for repeating

	./daemonresultsstageandsnapshot.sh

## Recording for live or test election 

	./daemonsnapshot.sh

# Replaying a recorded election 

If you're replaying, set

	export REPLAY_RACE_DATE=2016-02-20

	export SAVE_DATE=2016-02-11

	export SLEEP_TIME=60

And execute

	./daemonreplayresults.sh


