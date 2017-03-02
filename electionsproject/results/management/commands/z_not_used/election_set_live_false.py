from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from results.models import Election, ResultStage


# def load_result_archive(electiondate_arg):
#     ## stop pulling live data into stage, but don't truncate until archive data ready
#     ## pull in archived result
#     call_command('import_ap_elex', 'result', electiondate_arg)
#     call_command('import_ap_elex', 'result', election.electiondate) # , election.live ## do we need to pass live? if we do, right not it wouldn't necessary bc the correct "live" bc that field is based on whether we decide it is/consider it live, not AP
    
#     ## altho this shouldn't be needed, sleep before clearing ResultStage
#     sleep_time = (1800) ## 30 minutes
#     time.sleep(sleep_time)

# def clear_resultstage():
#     ## delete all objects from ResultStage after archive data loaded
#     resultstage_objects().delete()

# def clear_resultstage(electiondate_arg):
#     ## delete objects in ResultStage based on the date; why would this be needed? I don't remember
#     resultstage_objects().filter(electiondate=electiondate_arg).delete()

def election_set_live_false(electiondate_arg):
	## requisite vars
    now = timezone.now()
    election_objects = Election.objects.all()

'''
NEW WAY: or just how to do for auto?
'''
    
    election = election_objects.filter(live=True).filter(electiondate=electiondate_arg, dataentry="automated")
    ## or just use
    # election_obj(electiondate_arg)

    ## set false
    election.live = False
    election.save()
    print str(election) + " set live to FALSE"

    ## these are both imported from the file where they'll later be called from (election_auto), so probably best to just move to this file
    load_result_archive(electiondate_arg)
    clear_resultstage()

'''
OLD WAY: or just how to do for manual?
'''

    # ## set of live objects with endtime less than or equal to now
    # ## if logic set to switch to live=False when AP % = 100, then how to account for AP results that never reach 100%? set a time limit? then increase sleep time for import
    # elections_to_set_live_false = election_objects.filter(live=True).filter(endtime__lte=now) # .filter(starttime__lte=now) ## unneeded as filter? 

    # ## loop through each
    # for election in elections_to_set_live_false:
    #     ## set false
    #     election.live = False
    #     election.save()
    #     print str(election) + " set live to FALSE"

    #     ## these are both imported from the file where they'll later be called from (election_auto), so probably best to just move to this file
    #     load_result_archive(electiondate_arg)
    #     clear_resultstage()


    # for election in election_objects:

    #     if election.endtime:
    #         if election.endtime <= now:
    #             election.live = False
    #         ## pull in archived result
    #         # ./manage.py import_ap_elex result election.electiondate 


class Command(BaseCommand):
    help = 'Execute functions to set a manual Election live field as False based on starttime and endtime fields.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

    def handle(self, *args, **options):
        
        electiondate_arg = options['electiondate']
        print "Election date: \t\t" + electiondate_arg + "\n"

        election_set_live_false(electiondate_arg)

