from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core import serializers
from electionsproject.settings import mccelectionsenv, MCC_API_BASE_URL
from electionsproject.settings_private import CDN_DOMAIN
from results.slackbot import slackbot
from results.models import Race, ResultManual, ResultStage
import os
import json
import requests
import boto3


def json_to_s3(electiondate_arg, model_arg, test_arg, override_arg):

    ## GENERATE LIST OF RACES
    race_list = Race.objects.filter(electiondate=electiondate_arg)

    if test_arg and not override_arg:
         race_list.filter(test=True)

    number_of_races = race_list.count()

    message = 'Number of races:\t%s\n' % (number_of_races)
    slackbot(message)

    ## LOOP THRU RACES
    # counter_race = 0
    for race in race_list:
        # counter_race += 1

        race_id = race.raceid

        model = model_arg.lower()

        if model == 'resultstage' or model == 'resultlive':
            model = 'resultlive'
            model_url = 'result'
            results = ResultStage.objects.filter(raceid=race_id)

        elif model == 'resultmanual':
            model = 'resultmanual'
            model_url = 'result'
            results = ResultManual.objects.filter(raceid=race_id)

        ## this returns a list
        levels = results.order_by('level').distinct('level')
        ## this returns a dict
        # levels = results.order_by('level').distinct('level').values('level')

        # if counter_race == 1:
        #     levels_count = levels.count()

        #     message = '# of levels:\t\t%s\n' % (levels_count)
        #     slackbot(message)

        ## show all levels
        # if levels_count > 1:
        # counter_levels = 0
        for obj in levels:
            # counter_levels += 1
            
            level = obj.level

            # if counter_levels == 1:
            #     print 'Level:\t\t' + level + '\n'

            results_level = results.filter(level=level)
            
            ## GENERATE API URL
            query_string = 'raceid=' + race_id

            if mccelectionsenv.lower() == 'local':
                base_url = '<ADD URL HERE>'

            url = '%s/v1/%s/?format=json&level=%s&%s' % (base_url, model, level, query_string)

            # print 'API call:\n' + url

            # GRAB JSON
            response = requests.get(url)
            json_string = str(response.text)

            ## UPLOAD JSON TO S3
            path = ''

            ## check whether the item is marked as test or the test arg was passed
            if race.test or test_arg:
                path += 'test'

            ## set the strings for the URL
                ## it should be safe to include the electiondate and statepostal both here and in the embed bc why would those change? 
            electiondate_url = str(electiondate_arg).replace('-', '')
            statepostal_url = race.statepostal
            level_url = level.lower()
            raceid_url = race.raceid

            ## set the file name based on the race id
            # filename_s3 = 'elections/%s/%s/%s/%s/%s/%s.json' % (
            #     model_url, 
            #     electiondate_url,  
            #     test_status, 
            #     statepostal_url,
            #     level_url,
            #     raceid_url
            # )

            path = model_url + '/' + path

            ## works with embed
            filename_s3 = 'elections/%s/%s.json' % (
                path, 
                raceid_url
            )

            ## connect to S3
            s3 = boto3.resource('s3')

            ## upload the json string
            s3.Object('mccdata', filename_s3).put(Body=json_string)

            ## cdn domain for file url
            domain = CDN_DOMAIN

            ## url of the uploaded file
            url = domain + '/' + filename_s3

            # print "\nJSON uploaded to S3:\n%s\n" % url


class Command(BaseCommand):
    help = 'Get results json and publish to S3.'

    def add_arguments(self, parser):
        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )

        parser.add_argument('model', 
            help='Specify the model (result, resultstage, resultmanual) you want to grab and load'
        )

        parser.add_argument('-t' '--test',
            action='store_true',
            # type=str,
            dest='test',
            default=False,
            help="Specific whether it's a test or not"
        )

        parser.add_argument('-o' '--override',
            action='store_true',
            # type=str,
            dest='override',
            default=False,
            help="Override and force the results to be under test on S3"
        )

    def handle(self, *args, **options):
        electiondate_arg = options['electiondate']
        model_arg = options['model']
        test_arg = options['test']
        override_arg = options['override']

        if test_arg:
            test = '(test)'

        message = '\n------- JSON -> S3 for %s %s -------' % (model_arg, test)
        slackbot(message)

        print '\nElection date:\t\t%s' % (electiondate_arg)
        print 'Model:\t\t\t%s' % (model_arg)
        print 'Test?\t\t\t%s\n' % (test_arg)

        start_time = timezone.localtime(timezone.now())

        start_message = '\nStarted baking:\t\t' + str(unicode(start_time)) + '\n'

        message = start_message
        slackbot(message)

        ## *** FUNCTION CALL ***
        json_to_s3(electiondate_arg, model_arg, test_arg, override_arg)

        end_time = timezone.localtime(timezone.now())

        end_message = '\nFinished baking:\t' + str(unicode(end_time)) + '\n\n'
        bake_length = str(unicode(end_time - start_time)) 

        message = end_message
        slackbot(message)

        message = 'Bake length:\t\t' + bake_length
        slackbot(message)
        message = '--------------------------------------------------\n'
        slackbot(message)
