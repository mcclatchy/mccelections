from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.management import call_command
# from django.db.models import Sum, Avg
from results.models import ResultCsv, Result
from electionsproject.settings import mccelectionsenv
from results.slackbot import slackbot
import time


def load_resultcsv_to_result():

    ## queryset of objects to load
    resultcsv_objects = ResultCsv.objects.all()

    counter = 0

    for resultcsv in resultcsv_objects:

        resultcsv_mapping = {
            'dataentry': "manual",
            # 'datasource': "",
            'ballotorder': resultcsv.ballotorder,
            # 'description': resultcsv.description,
            'electiondate': resultcsv.electiondate,
            'fipscode': resultcsv.fipscode, 
            'first': resultcsv.first, 
            # 'gdoc_import': True,
            'id': resultcsv.id,
            'incumbent': resultcsv.incumbent,
            'is_ballot_measure': resultcsv.is_ballot_measure,
            'last': resultcsv.last,
            'lastupdated': resultcsv.lastupdated,
            'level': resultcsv.level, 
            'note': resultcsv.note,
            'officename': resultcsv.officename,
            # 'nonpartisan': resultcsv.nonpartisan, ## needs to be uncommented in Result master model
            'party': resultcsv.party, 
            'precinctsreporting': resultcsv.precinctsreporting,
            'precinctsreportingpct': resultcsv.precinctsreportingpct,
            'precinctstotal': resultcsv.precinctstotal,
            'racetype': resultcsv.racetype,
            'reportingunitname': resultcsv.reportingunitname,
            'seatname': resultcsv.seatname,
            'seatnum': resultcsv.seatnum,
            'statepostal': resultcsv.statepostal, 
            # 'test': resultcsv.test, ## this isn't in the gdoc sheet, as of now
            'uncontested': resultcsv.uncontested,
            'votecount': resultcsv.votecount,
            'votepct': resultcsv.votepct,
            # 'votingsystem': result.votingsystem, ## needs to be uncommented in Result master model
            'winner': resultcsv.winner
        }

        ## load/create
        obj, created = Result.objects.update_or_create(**resultcsv_mapping)       

        counter += 1

    message = "\nLoaded:\t\t\t" + str(counter) + " results loaded from ResultCsv to Result archive"
    slackbot(message)


class Command(BaseCommand):
    help = 'Load ResultCsv into Result archive.'

    def add_arguments(self, parser):
        ## required argument
        parser.add_argument('date', 
            help='Specify the date.'
        )

    def handle(self, *args, **options):

        date_arg = options['date']
        message = "Election date: \t\t" + date_arg
        slackbot(message)

        ## delete existing? nope, because the date here isn't a real election date, at least for now
        # Result.objects.filter(dataentry="manual", election_date=date_arg)

        ## import gdoc to ResultCsv
        call_command('csv_import', date_arg)

        ## import ResultCsv to Result archive
        load_resultcsv_to_result()
