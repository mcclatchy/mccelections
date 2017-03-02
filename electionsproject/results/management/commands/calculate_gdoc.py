from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum 
from django.utils import timezone
from results.models import ResultManual
from results.slackbot import slackbot
from results.calculations import calculated_percent


def calculate_precinctsreportingpct(electiondate_arg):
    gdoc_results = ResultManual.objects.filter(electiondate=electiondate_arg, gdoc_import=True)

    message = "precinctsreportingpct"
    slackbot(message)
    start_time = timezone.localtime(timezone.now())
    start_message = '\nStarted calculations:\t' + str(unicode(start_time))
    message = start_message
    slackbot(message)

    for result in gdoc_results:
	    if result.precinctsreporting:        
	        result.precinctsreportingpct = calculated_percent(result.precinctsreporting, result.precinctstotal)
	    elif result.precinctsreporting == None:
	        result.precinctsreportingpct = None

	    result.save()

    end_time = timezone.localtime(timezone.now())
    end_message = '\nFinished calculations:\t' + str(unicode(end_time)) + '\n'
    import_length = str(unicode(end_time - start_time)) 
    message = end_message
    slackbot(message)
    message = 'Import length:\t\t' + import_length
    slackbot(message)

def calculate_votepct(electiondate_arg):
    gdoc_results = ResultManual.objects.filter(electiondate=electiondate_arg, gdoc_import=True)

    calculated_total_votes_dict_list = gdoc_results.values('raceid').annotate(vote_count_total=Sum('votecount'))

    message = "\n\nvotepct"
    slackbot(message)
    start_time = timezone.localtime(timezone.now())
    start_message = '\nStarted calculations:\t' + str(unicode(start_time))
    message = start_message
    slackbot(message)

    ## if there are any ResultManual objects that are from a gdoc import
    if gdoc_results:
        ## set up a new empty dict 
        calculated_total_votes_dict = {}
        ## loop thru the list of dicts with raceids and vote totals to extract and add the relevant key/value pairs
        for item in calculated_total_votes_dict_list:
            calculated_total_votes_dict[item['raceid']] = item['vote_count_total']
        ## loop thru the results
        for resultmanual_obj in gdoc_results:
            ## get the raceid
            resultmanual_obj_race_id = resultmanual_obj.raceid
            ## get the vote total
            vote_total = calculated_total_votes_dict[resultmanual_obj_race_id]
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
    help = 'Calculate precincts reporting percent for ResultManual object imported from a Google Doc.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

    def handle(self, *args, **options):
        ## get election date argument
        electiondate_arg = options['electiondate']
        
        message = "\n--------------- CALCULATE GDOC RESULTS ---------------\n"
        slackbot(message)

        message = "Election date: \t\t" + electiondate_arg + "\n\n"
        slackbot(message)

        ## call the functions
        calculate_precinctsreportingpct(electiondate_arg)

        calculate_votepct(electiondate_arg)

