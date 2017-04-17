from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from results.models import Election, ResultCsv#, ResultCsvCheck
from results.slackbot import slackbot
from django.db import connection
from subprocess import call
import psycopg2
import urllib2
import os


## pass url as an arg or just include in the function?
def import_csv(electiondate_arg):
    psql_connection = os.environ["PSQL_CONNECTION"]
    file_path = os.environ["SAVER_PATH"]
    filename = file_path + "/tmp/gdocresults.csv"

    ## make sure the necessary vars are populated
    if not psql_connection:
        message = "Please add the following to ~/.bashrc: export PSQL_CONNECTION=\"<connection info here>\""
        slackbot(message)

    if not file_path:
        message = "Please add the file path to ~/.bashrc based on current environment."
        slackbot(message)

    ## QUESTION: add a filter for "live"? if so, will user flip that or will be done automatically? (e.g. via start/end time or looking if votecount for a state is greater than zero) 
        ## Yes, I've added this so the script doesn't get tripped up if there are both test and non-test election objects created
    elections = Election.objects.filter(dataentry="manual", electiondate=electiondate_arg, live=True, url__contains="output=csv")
    elections_count = elections.count()

    if elections_count > 1:
        message = "\nWARNING: There's more than one manual election entered on this date. Please resolve this issue and re-run the command.\n"
        slackbot(message)
    elif not elections_count:
        message = "\nWARNING: There are no Google sheet URLs filled out for this election date. Please check the election, add/fix and re-run this script.\n"
        slackbot(message)
    elif elections_count == 1:
        election = elections[0]
        gdoc_url = election.url
        ## example url
        # gdoc_url = "https://docs.google.com/spreadsheets/d/1UpetYYiZ0PctgeZM5eBwSlO3p0QtbHEwHlQtdjBllls/pub?gid=0&single=true&output=csv"

        ## parse the ID's out and then construct url with the template url? could be a good back-up if user enters non-CSV url

        ## construct the url
        # gdoc_id_string = "1UpetYYiZ0PctgeZM5eBwSlO3p0QtbHEwHlQtdjBllls"
        # gdoc_gid_string = "0"
        # gdoc_url = "https://docs.google.com/spreadsheets/d/%s/pub?gid=%s&single=true&output=csv" % (gdoc_id_string, gdoc_gid_string)

        if gdoc_url:

            message = "\nAbove to save CSV..."
            slackbot(message)

            ## grab the contents
            response = urllib2.urlopen(gdoc_url)
            
            ## save the url to a file
            filehandler = open(filename, "w")
            filehandler.write(response.read())
            filehandler.close()
            message = "Saved:\t" + str(filename) + "\n"
            slackbot(message)

            ## load whatever existing ResultCsv objects to ResultManual + archive before truncating ???
                # I don't think this works bc it needs the last election data that's in there -- not the current
            # call_command("import_ap_elex", "resultmanual", electiondate_arg)

            def resultcsv_count():
                resultcsv_count = ResultCsv.objects.all().count()
                return resultcsv_count

            ## truncate results_resultcsv table
            pre_count = resultcsv_count()
            truncate_sql = "\"TRUNCATE TABLE results_resultcsv CASCADE;\""
            truncate_command = psql_connection + " " + truncate_sql
            message = "About to remove old results from ResultCsv table..."
            slackbot(message)
            ## pass this to subprocess
            call(truncate_command, shell=True)
            message = "ResultCsv delete:\t%s" % (pre_count)
            slackbot(message)

            ## load data via psql to results_resultcsv table
            cursor = connection.cursor()

            message = "\nAbout to load data to ResultCsv table..."
            slackbot(message)

            copy_sql = '''
                        COPY results_resultcsv FROM stdin DELIMITER ',' CSV HEADER;
                        '''
            with open(filename, 'r') as f:
                cursor.copy_expert(sql=copy_sql, file=f)
                connection.commit()
                cursor.close()
            post_count = resultcsv_count()
            message = "ResultCsv loaded:\t%s\n" % (post_count)
            slackbot(message)

            # update result count field on the related Election
            election.resultcount = post_count
            election.save()

        else:
            message = "\nNo Google Doc URL provided for election on %s.\n" % (electiondate_arg)
            slackbot(message)


class Command(BaseCommand):
    help = 'Import results data from Google doc spreadsheet.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

    def handle(self, *args, **options):

        message = "\n-------------- gdoc import to ResultCsv --------------"
        slackbot(message)

        electiondate_arg = options['electiondate']
        message = "\nElection date: \t\t" + electiondate_arg
        slackbot(message)

        import_csv(electiondate_arg)

