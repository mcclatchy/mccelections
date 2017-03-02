from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from results.models import Election
from django.utils import timezone
from results.slackbot import slackbot
import time ## used for sleep


## this was made into a function just so it'd be easier to test on CLI or call on its own
def download_elections_core_models():
    message = "\n------------- DOWNLOADING ELECTIONS -------------"
    slackbot(message)

    ## call mgmt command to import elections; 2016 is abritrary unused value just to meet req for positional arg
    call_command('import_ap_elex', 'election', '2016')

    def load_races_candidates():
        # today = timezone.now().date() ## this gives GMT date
        today = timezone.localtime(timezone.now()).date() ## this gives actual NY date
        elections_new = Election.objects.filter(created__gt=today, title__contains="Automated")

        number_of_elections = len(elections_new)
        counter = 0

        ## loop through election imported today
        for election in elections_new:
            ## set election date
            electiondate = str(election.electiondate)

            message = "\n---------- DOWNLOADING RACES/CANDIDATES ---------"
            slackbot(message)

            ## load candidates and races
            if str(electiondate) == str(today):
                call_command('import_ap_elex', 'race', electiondate)
                call_command('import_ap_elex', 'candidate', electiondate)
            else:
                call_command('import_ap_elex', 'race', electiondate, '-t')
                call_command('import_ap_elex', 'candidate', electiondate, '-t')
            
            counter += 1

            if counter != number_of_elections:
                ## sleep this loop to avoid maxing out AP API calls
                sleep_time = 30
                message = "Sleeping for %s seconds" % (sleep_time)
                slackbot(message)
                time.sleep(sleep_time)
    
    load_races_candidates()

class Command(BaseCommand):
    help = 'Loads Elections from AP, then loads related races and candidates for each.'

    def handle(self, *args, **options):    

        download_elections_core_models()

