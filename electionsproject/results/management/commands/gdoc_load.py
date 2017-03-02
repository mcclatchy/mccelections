from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from results.slackbot import slackbot


class Command(BaseCommand):
    help = 'Loads ResultCsv from gdoc manual and races from ResultCsv.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

    def handle(self, *args, **options):   
        electiondate_arg = options['electiondate']

        ## load gdoc into ResultCsv
        call_command("csv_import", electiondate_arg)

        ## load distinct races from ResultCsv into Races
        # from results.election_loaders import load_resultcsv_to_race
        message = "\n---------- ResultCsv import to Races ------------"
        slackbot(message)
        call_command("import_ap_elex", "resultcsv2race", electiondate_arg)