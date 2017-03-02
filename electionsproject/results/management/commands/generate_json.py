from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core import serializers
from results.models import Result, ResultManual, ResultStage, Race
from results.slackbot import slackbot
from results.s3connection import s3_connection
import os


def generate_json(electiondate_arg, model_arg):

    message = 'Model:\t\t\t%s' % (model_arg)
    slackbot(message)

    ## path where files are saved
    file_path = os.environ['SAVER_PATH']

    ## get and output the number of races
    race_list = Race.objects.filter(electiondate=electiondate_arg)
    number_of_races = race_list.count()

    message = 'Number of races:\t\t' + str(number_of_races)
    slackbot(message)

    ## loop thru the races
    for race in race_list:

        message = '\n' + str(race) + '\n'
        slackbot(message)

        ## filename based on electiondate, statepostal, raceid
        filename = str(race.electiondate).replace('-', '') + '-' + race.statepostal + '-' + str(race.raceid) + '.json'

        ## local file to use for storing json until copied to S3
        json_file = file_path + '/tmp/' + filename

        ## filter object set for the given model by election date, raceid and level
        if model_arg == 'result' or model_arg == 'Result':
            objects = Result.objects.filter(electiondate=electiondate_arg, raceid=race.raceid, level="state")

        elif model_arg == 'resultmanual' or model_arg == 'ResultManual':
            objects = ResultManual.objects.filter(electiondate=electiondate_arg, raceid=race.raceid, level="state")

        elif model_arg == 'resultstage' or model_arg == 'ResultStage':
            objects = ResultStage.objects.filter(electiondate=electiondate_arg, raceid=race.raceid, level="state")
        
        # elif model_arg == 'race' or model_arg == 'Race':
        #     objects = Race.objects.filter(electiondate=electiondate_arg, raceid=race.raceid)#, level="state")

        ## get and output the number of objects
        number_of_objects = objects.count()

        # message = 'Number of objects:\t\t%s' % (str(number_of_objects))
        # slackbot(message)

        ## serialize as json
        json_output = serializers.serialize('json', objects)

        ## create file for each
        with open(json_file, 'wb') as file:
            file.write(json_output)
        
        ## construct a new filename for S3
        filename_formatted = filename.replace('-', '/')
        filename_s3 = 'elections/results/' + filename_formatted

        # ## save the file to s3
        with open(json_file,'rb') as file_to_upload:
            s3_connection().upload(filename_s3, file_to_upload)
        
        # ## delete the file
        os.remove(json_file)


class Command(BaseCommand):
    help = 'Generate JSON based on a model.'

    def add_arguments(self, parser):
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

        parser.add_argument('model', 
            help='Specify the model (result, resultstage, resultmanual, etc) you want to grab and load'
        )

    def handle(self, *args, **options):
        electiondate_arg = options['electiondate']
        model_arg = options['model']

        start_time = timezone.localtime(timezone.now())

        start_message = '\nStarted generating:\t\t' + str(unicode(start_time)) + '\n'

        message = start_message
        slackbot(message)

        generate_json(electiondate_arg, model_arg)

        end_time = timezone.localtime(timezone.now())

        end_message = '\nFinished generating:\t\t' + str(unicode(end_time)) + '\n\n'
        generate_length = str(unicode(end_time - start_time)) 

        message = end_message
        slackbot(message)

        message = 'Generate length:\t\t' + generate_length
        slackbot(message)
        message = '--------------------------------------------------\n'
        slackbot(message)