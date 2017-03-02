from django.core.management.base import BaseCommand, CommandError
from results.models import ReportingUnit, ResultManual
import time
from results.slackbot import slackbot
from electionsproject.settings import mccelectionsenv


def replay_resultmanual():
    
    test_length = 36
    while (test_length > 0):
        ## fix electiondate reference
        reportingunits = ReportingUnit.objects.filter(dataentry="manual") # test=True #.filter(election_fk__electiondate="2016-03-15") 
        manualresults = ResultManual.objects.filter(dataentry="manual") # test=True #.filter(election_fk__electiondate="2016-03-15")

        test_steps = [1, 2, 3, 4, 5, 6, 7, 8 , 9, 10]

        for item in test_steps:

            message = str(item) + "\n"
            slackbot(message)
            
            if item == 1:
                manualresults.update(precinctsreporting=0)
                manualresults.update(precinctsreportingpct=0)
                manualresults.update(votecount=0)
                manualresults.update(votepct=0)
                
                message = "Values reset \n"
                slackbot(message)

            else:
                total_ru = item * 10
                message = total_ru
                slackbot(message)
                
                total_rm = item * 100
                message = total_rm
                slackbot(message)

                manualresults.update(precinctsreporting=total_ru)
                manualresults.update(precinctsreportingpct=total_ru)
                manualresults.update(votecount=total_rm)
                manualresults.update(votepct=50)
                
                message = "Updated manual results and reporting units"
                slackbot(message)
            
            ## sleep
            time.sleep(60)
        test_length = test_length - 1
        message = "Restarting test loop \n\n"
        slackbot(message)

class Command(BaseCommand):
    help = 'Simulate a manual result test'

    def handle(self, *args, **options):
        
        if mccelectionsenv != "prod":
            replay_resultmanual()
        else:
            message = "WARNING: You're on the production server, so this won't execute."
            slackbot(message)
