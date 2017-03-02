from django.core.management.base import BaseCommand, CommandError
from results.models import ReportingUnit, ResultManual
from results.slackbot import slackbot


class Command(BaseCommand):
    help = 'Sync precincts reporting for ReportingUnit and ResultManual.'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id',
            # action='store_true',
            type=int,
            dest='id',
            # default=False,
            help='This is the ID from the related object.'
        )

    def handle(self, *args, **options):

    	id_arg = options['id']