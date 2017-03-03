from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from electionsproject.settings import MCC_API_BASE_URL, mccelectionsenv
from results.slackbot import slackbot
from results.models import Race
from results.s3connection import s3_connection
import os
import requests


def bake_api_to_static(electiondate_arg, model_arg):

    ## path where files are saved
    file_path = os.environ['SAVER_PATH']

    ## get and output the number of races
    race_list = Race.objects.filter(electiondate=electiondate_arg)
    number_of_races = race_list.count()

    message = 'Number of races:\t\t' + str(number_of_races)
    slackbot(message)

    ## loop thru races, which is if we want to do this after a complete data pull
    for race in race_list:

        message = '\n' + str(race) + '\n'
        slackbot(message)

        ## filename based on electiondate, statepostal, raceid
        filename = str(race.electiondate).replace('-', '') + '-' + race.statepostal + '-' + str(race.raceid) + '.json'
        # print filename
        ## mimick old structure
        # filename = '?raceid=' + race.raceid
        ## local file to use for storing json until copied to S3
        json_file = file_path + '/tmp/' + filename
        # print '\n' + json_file

        ## form the endpoint url
        query_string = 'raceid=' + race.raceid
        ## if it's not prod, use the test API bc we can't curl the localhost one
        if mccelectionsenv != 'prod':
            MCC_API_BASE_URL = 'http://<YOUR_DOMAIN>.com/api'
        ## lowercase the model name to make sure it works in the URL
        model = model_arg.lower()
        ## swap resultstage, which is the correct model name, with resultlive, which is the resource/endpoint name
        if model == 'resultstage' or model == 'ResultStage':
            model = 'resultlive'
        ## full url to download
        url = '%s/v1/%s/?format=json&level=state&%s' % (MCC_API_BASE_URL, model, query_string)        
        # print url + '\n'

        ## grab the file contents and write to a file
        response = requests.get(url)
        text = response.text
        with open(json_file, 'wb') as f:
            f.write(text)

        # message = "- Grabbed the json"
        # slackbot(message)

        ## constructing query_string_info to help make URL evident without needing to load; different than query_string for hitting API
        # query_string_info = '?%s&%s' % (race.racetype, race.officename)
        # if race.seatname:
        #     query_string_info += '&%s' % (race.seatname)
        # if race.party:
        #     query_string_info += '&%s' % (race.party)
        # query_string_info = query_string_info.replace(" ", "%20")
        # query_string_info = query_string_info.replace("&", "%26")

        ## construct a new filename for S3
        filename_formatted = filename.replace('-', '/')
        filename_s3 = 'elections/results/' + filename_formatted # + query_string_info
        # print filename_s3
        ## upload the json file
        with open(json_file,'rb') as file_to_upload:
            s3_connection().upload(filename_s3, file_to_upload)

        # message = '- Copied to S3'
        # slackbot(message)

        ## delete the json file
        os.remove(json_file)

        # message = '- Deleted the local file\n'
        # slackbot(message)

class Command(BaseCommand):
    help = 'Construct API URL, save json and publish to S3.'

    def add_arguments(self, parser):
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

        parser.add_argument('model', 
            help='Specify the model (result, resultstage, resultmanual) you want to grab and load'
        )

    def handle(self, *args, **options):
        electiondate_arg = options['electiondate']
        model_arg = options['model']

        start_time = timezone.localtime(timezone.now())

        start_message = '\nStarted baking:\t\t' + str(unicode(start_time)) + '\n'

        message = start_message
        slackbot(message)

        bake_api_to_static(electiondate_arg, model_arg)

        end_time = timezone.localtime(timezone.now())

        end_message = '\nFinished baking:\t' + str(unicode(end_time)) + '\n\n'
        bake_length = str(unicode(end_time - start_time)) 

        message = end_message
        slackbot(message)

        message = 'Bake length:\t\t' + bake_length
        slackbot(message)
        message = '--------------------------------------------------\n'
        slackbot(message)
