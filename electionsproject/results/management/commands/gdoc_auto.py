from django.core.management.base import BaseCommand, CommandError
# from django.utils import timezone
from django.core.management import call_command
from results.models import Election
from results.slackbot import slackbot
import time


'''
convert to mgmt command and then fire on each Election (gdoc manual) save (when Live is True)?

ok, here's what we need:

if Live is True and url exists, fire on Election save

to avoid issues with additonal saves, need a way to see what the previous state was (if Live was False before, then fire; if Live was True before, then don't fire)

'''

class Command(BaseCommand):
    help = 'Checks if gdoc manual election is live.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

    def handle(self, *args, **options):   
        electiondate_arg = options['electiondate']

        # today_string = str(timezone.localtime(timezone.now()).date())

        ## exclude automated elections and election w/ empty URL field
        elections = Election.objects.filter(electiondate=electiondate_arg, url__contains="output=csv").exclude(dataentry="automated")

        message = "\n----------------- MANUAL GDOC IMPORT -----------------\n"
        slackbot(message)

        if elections.count() > 1: 
            message = "WARNING: More than one gdoc manual election today specified. Please fix in the admin!\n"
            slackbot(message)
            for election in elections:
                slackbot(election)
                slackbot(election.url)
                slackbot("\n")                
        elif not elections: 
            message = "No gdoc manual election today on %s.\n" % (electiondate_arg)
            slackbot(message)
        elif elections.count() == 1:
            message = "One gdoc manual election today on %s.\n" % (electiondate_arg)
            election = elections[0]
            election_live = election.live
            slackbot(message)

            while election_live:
                ## load gdoc into ResultCsv
                call_command("csv_import", electiondate_arg)

                ## load ResultCsv into ResultManual
                message = "\n---------- ResultCsv import to ResultManual ------------"
                slackbot(message)
                call_command("import_ap_elex", "resultmanual", electiondate_arg)

                ## calculate votepct and precinctsreportingpct
                call_command("calculate_gdoc", electiondate_arg)

                ## load distinct races from ResultCsv into Races
                from results.election_loaders import load_resultcsv_to_race
                message = "\n---------- ResultCsv import to Races ------------"
                slackbot(message)
                call_command("import_ap_elex", "resultcsv2race", electiondate_arg)

                ## load ResultCsv into Result archive
                # message = "\n---------- ResultCsv import to Result archive ------------"
                # slackbot(message)
                # call_command("import_ap_elex", "resultmanual2result", electiondate_arg)

                sleep_time = 60
                message = "Sleeping for %d seconds\n" % (sleep_time)
                slackbot(message)
                time.sleep(sleep_time)

            if not election_live:
                message = "Not live yet:\t\t%s\n" % (election)
                slackbot(message)
