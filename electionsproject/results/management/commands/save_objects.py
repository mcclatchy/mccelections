from django.core.management.base import BaseCommand, CommandError
from results.models import Race, ReportingUnit, ResultManual #, Embed
# from results.slackbot import slackbot


# # def save_models(election_date_arg, dataentry_arg):
def save_models():

#     election_date_arg = "2016-11-08"
#     dataentry_arg = "manual"

#     ## querysets 

#     races = Race.objects.filter(electiondate=election_date_arg, dataentry=dataentry_arg)

#     reportingunits = ReportingUnit.objects.filter(electiondate=election_date_arg, dataentry=dataentry_arg)

#     results = ResultManual.objects.filter(electiondate=election_date_arg)

#     # embeds = Embed.objects.filter(electiondate="2016-11-08")

#     ## save loops
  
#     message = "--------- RACES -------"
#     slackbot(message)

#     race_count = race.count()

#     message = "About to save:\t\t%s" % (race_count)
#     slackbot(message)

#     for race in races:
#         race.save()
 
#     message = "--------- REPORTING UNITS -------"
#     slackbot(message)

#     reportinunit_count = race.count()

#     message = "About to save:\t\t%s" % (reportinunit_count)
#     slackbot(message)

#     for reportingunit in reportingunits:
#         reportingunit.save()

#     message = "--------- RESULTS -------"
#     slackbot(message)

#     result_count = race.count()

#     message = "About to save:\t\t%s" % (result_count)
#     slackbot(message)

#     for result in results:
#         result.save()
    
#     # message = "--------- EMBEDS -------"
#     # slackbot(message)

#     # embed_count = race.count()

#     # message = "About to save:\t\t%s" % (embed_count)
#     # slackbot(message)

#     # for embed in embeds:
#     #     embed.save()


class Command(BaseCommand):
    help = 'Save objects for all the specified models.'

#     # def add_arguments(self, parser):
#     #     ## positional requred arguments
#     #     # parser.add_argument('electiondate', 
#     #     #     help='Specify the election date as YYYY-MM-DD'
#     #     # )

#     #     ## named, optional arguments
#     #     parser.add_argument('-e', '--electiondate',
#     #         action='store_true',
#     #         dest='electiondate',
#     #         # default=False,
#     #         help='Specify the election date as YYYY-MM-DD'
#     #     )

#     #     parser.add_argument('-d', '--dataentry',
#     #         # action='store_true',
#     #         type=str,
#     #         dest='dataentry',
#     #         # default=False,
#     #         help='Specify the date as YYYY-MM-DD'
#     #     )

    def handle(self, *args, **options):

        election_date_arg = "2016-11-08"
        dataentry_arg = "manual"

        ## querysets 

        races = Race.objects.filter(electiondate=election_date_arg, dataentry=dataentry_arg)

        reportingunits = ReportingUnit.objects.filter(electiondate=election_date_arg, dataentry=dataentry_arg)

        results = ResultManual.objects.filter(electiondate=election_date_arg)

        # embeds = Embed.objects.filter(electiondate="2016-11-08")

        ## save loops

        message = "--------- RACES -------"
        slackbot(message)

        race_count = race.count()

        message = "About to save:\t\t%s" % (race_count)
        slackbot(message)

        for race in races:
            race.save()

        message = "--------- REPORTING UNITS -------"
        slackbot(message)

        reportinunit_count = race.count()

        message = "About to save:\t\t%s" % (reportinunit_count)
        slackbot(message)

        for reportingunit in reportingunits:
            reportingunit.save()

        message = "--------- RESULTS -------"
        slackbot(message)

        result_count = race.count()

        message = "About to save:\t\t%s" % (result_count)
        slackbot(message)

        for result in results:
            result.save()

#         # electiondate_arg = options['electiondate']
#         # dataentry_arg = options['dataentry']

#         # if electiondate_arg:
#         #     message = "\nElection date: \t\t" + str(electiondate_arg)
#         #     slackbot(message)
#         # else: 
#         #     electiondate_arg = "2016-11-08"

#         # if dataentry_arg:
#         #     message = "\nData entry: \t\t" + str(dataentry_arg)
#         #     slackbot(message)
#         # else:
#         #     dataentry_arg = "manual"

#         # save_models(electiondate_arg=electiondate_arg, dataentry_arg=dataentry_arg)
#         save_models()
