from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum 
from django.utils import timezone
from results.models import ResultManual
from results.slackbot import slackbot
from results.calculations import calculated_percent


def update_vote_percent(electiondate_arg):

    ## all ResultManual objects that aren't zero (bc we can't divide with 0) or from a gdoc 
    resultmanual_objects = ResultManual.objects.filter(electiondate=electiondate_arg, votecount__gt=0).exclude(gdoc_import=True)

    ## all total vote count by race
    calculated_total_votes_dict_list = resultmanual_objects.values('race_name_fk').annotate(vote_count_total=Sum('votecount'))

    start_time = timezone.localtime(timezone.now())
    start_message = '\nStarted calculations:\t' + str(unicode(start_time))
    message = start_message
    slackbot(message)

    ## if there are any ResultManual objects that aren't from a gdoc import
    if resultmanual_objects:
        ## set up a new empty dict
        calculated_total_votes_dict = {}
        ## loop thru the list of dicts with raceids and vote totals to extract and add the relevant key/value pairs
        for item in calculated_total_votes_dict_list:
            calculated_total_votes_dict[item['race_name_fk']] = item['vote_count_total']
        ## loop thru the results
        for resultmanual_obj in resultmanual_objects:
            ## get the race FK id
            resultmanual_obj_raecid = resultmanual_obj.race_name_fk.id
            ## get the vote total
            vote_total = calculated_total_votes_dict[resultmanual_obj_raecid]
            ## get the vote count
            vote_count = resultmanual_obj.votecount
            ## calculate the percent
            percent_calculated = calculated_percent(vote_count, vote_total)
            ## get the object id
            resultmanual_obj_id = resultmanual_obj.id
            ## update the object
            ResultManual.objects.filter(id=resultmanual_obj_id).update(votepct=percent_calculated)

    end_time = timezone.localtime(timezone.now())
    end_message = '\nFinished calculations:\t' + str(unicode(end_time)) + '\n'
    import_length = str(unicode(end_time - start_time)) 
    message = end_message
    slackbot(message)
    message = 'Import length:\t\t' + import_length + '\n'
    slackbot(message)


class Command(BaseCommand):
    help = 'Calculate total votes per race and update each ResultManual object'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

    def handle(self, *args, **options):
        ## get election date argument
        electiondate_arg = options['electiondate']

        message = "\n------------ CALCULATE MANUAL ADMIN RESULTS ------------\n"
        slackbot(message)

        message = "Election date: \t\t" + electiondate_arg
        slackbot(message)

        update_vote_percent(electiondate_arg)

