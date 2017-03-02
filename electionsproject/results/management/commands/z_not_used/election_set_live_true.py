from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from results.models import Election, ResultStage


## how to call this? from scheduler based on... the date? the date & time? if latter, then why not move that to scheduler?
def election_set_live_true():
    ## requisite vars
    now = timezone.now()
    election_objects = Election.objects.all()
   
    ## INCOMPLETE: the following endtime_exists and condition check don't work!
    # endtime_exists = election_objects.exclude(live=True).filter(endtime__gt=0) ## this throw an error 

    # if endtime_exists.count() >= 1:
    #     ## election objects that do have end times
    #     election_objects_to_set_live = election_objects.exclude(live=True).filter(starttime__lte=now).filter(endtime__gt=now)
    # else:
        ## to account for election objects that might not have end times
        # election_objects_to_set_live = election_objects.exclude(live=True).filter(starttime__lte=now)

    ## excludes automated elections
    elections_to_set_live_true = election_objects.exclude(live=True, dataentry="automated").filter(starttime__lte=now)

    # state_level_resultstage = ResultStage.objects.filter(level=state)

    ## !!!!! ADD CONDITIONAL (as an "or" clause?): IF PRECINCTREPORTING IS GREATER THAN ZERO, THEN SET LIVE !!!!!!
        ## this also needs to look at if a winner is set and update that info bc sometimes AP calls winners before any data exists in the system

    ## loop through each Election object with start time as now or just past
        ## BETTER SOLUTION? regularly check to see if AP results for that date are precinctsreporting__gte=0 or votecount__gte=0; initially, I thought that should use level="state", but we probably need to account for elections that don't have any state-level results (e.g. local races)
    for election in elections_to_set_live_true:
        print ""
        print election
        ## use/update this if we're using endtime field
        if election.endtime and election.endtime > now:
            election.live = True
            election.save()
            print "SAVED:\t\t\t" + str(election) + " (already had end time)"
        elif not election.endtime:
            election.live = True
            ## GOAL: switch endtime update with code below to check precinctsreportingpct
                ## also possible: populate via a Duration field in an settings model for admins
            # election.endtime = now
            print "Setting new endtime: " + str(election.endtime)
            election.endtime += timedelta(hours=12)
            print "Adding 12 hours to that: " + str(election.endtime)
            election.save()
            print "SAVED:\t\t\t" + str(election) + " (programmatically added an end time)"
        print ""

        ## another option would be just to match the electiondate, but! election results might still flow on the following 1-2 days or more
        # for result in state_level_resultstage:
        #     if result.electionday == election.elecdate and result.precinctsreportingpct < 100
        #         election.live = True

        ## use/update this if checking for 100 percent reporting, which probably requires
            ## changing ResultStage to ResultElex table, which maps to Elex fields exactly
            ## making a new ResultStage that inherits from ResultLive(?)
            ## coping ResultElex to new ResultStage and, in the process, connecting the foreign keys, most importantly for Race and ReportingUnits
            ## flowing ResultStage to ResultLive via inheritance or copying
        # election_races = election.race_set.all()
        # for race in election_races:
        #     election_race_reportingunit = race.reportingunit_set.all()
        #     for reportingunit in election_race_reportingunit:
        #         filtered_reportingunits = reportingunit.filter(level=state) 
        #             for result in filtered_reportingunits.all():
        #                 if result.precinctsreportingpct < 100
        #                     election.live = True
        

    ## loop through each Election object
    # for election in election_objects:
    #     ## it's essential to include election.starttime bc this queryset includes all objects
    #     if election.starttime and election.endtime:
    #         if election.starttime >= now and now <= election.endtime:
    #             election.live = True
    #     elif election.starttime and not election.endtime:
    #          if election.starttime >= now:
    #             election.live = True
    #             # election.endtime += timedelta(hours=10) ## eventually abstract this to a Defaults class? idk!


class Command(BaseCommand):
    help = 'Execute functions to set a manual Election live field as True based on starttime and endtime fields.'

    def handle(self, *args, **options):
        
        election_set_live_true()

