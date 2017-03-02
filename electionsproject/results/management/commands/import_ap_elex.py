from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from results.models import Candidate, Race, Result, Election, ResultManual, ResultStage, ResultCheck
from results.slackbot import slackbot
from django.utils import timezone
from subprocess import call
import requests
import os


'''
Functions for core models: Candidate, Race, Result
'''

def delete_filtered(self, model_arg, electiondate_arg):
    if model_arg == "race":
        objects_filtered = Race.objects.filter(electiondate=electiondate_arg).exclude(dataentry="manual")
    elif model_arg == "result":
        objects_filtered = Result.objects.filter(electiondate=electiondate_arg).exclude(dataentry="manual")
    elif model_arg == "candidate":
        objects_filtered = Candidate.objects.filter(electiondate=electiondate_arg).exclude(dataentry="manual")
    # elif model_arg == "election":
        # today_date = str(timezone.localtime(timezone.now()).date())
        # today = int(today_date.replace("-", ""))
        # objects_filtered = Election.objects.filter(id__gte=today).exclude(dataentry="manual") ## UPDATE: make sure deletes any election on today so that one can be loaded anew
    elif model_arg == "resultmanual":
        ## this will only work if nothing is being entered into the admin for that electiondate; otherwise, it deletes everything and that would be a major problem
            ## does adding the gdoc_import=True solive that?
        objects_filtered = ResultManual.objects.filter(electiondate=electiondate_arg, gdoc_import=True)
    elif model_arg == "resultcsv2race":
        objects_filtered = Race.objects.filter(electiondate=electiondate_arg, dataentry="manual", gdoc_import=True)
    elif model_arg == "resultcsv2check":
        objects_filtered = ResultCheck.objects.filter(electiondate=electiondate_arg, gdoc_import=True)
    # elif model_arg == "resultcsv2result":
    #     objects_filtered = Result.objects.filter(electiondate=electiondate_arg, dataentry="manual") # gdoc_import=True, ## using that would require adding that field to Result and removing from ResultManual, then migrating

    if model_arg != "election":
        objects_filtered_count = objects_filtered.count()
        message = "About to delete objects..."
        slackbot(message)

        objects_filtered.delete()
        objects_deleted_message = "Deleted:\t\t%s %s objects" % (objects_filtered_count, model_arg)
        
        message = objects_deleted_message + "\n"
        slackbot(message)


def load_model(electiondate_arg, model_arg, live_arg, test_arg, all_arg):
    from results.election_loaders import load_data_candidates, load_data_races, load_data_results, load_data_all, load_data_elections, load_resultcsv_to_resultmanual, load_resultcsv_to_race, load_resultcsv_to_resultcheck # , load_resultcsv_to_result
    from results.elexconnection import election_connection

    params = (electiondate_arg, live_arg, test_arg) # all_arg ## include if we're filtering races and candidates by the specified states

    ## function calls based on model
    if model_arg == "race" or model_arg == "races":
        load_data_races(*params)
    elif model_arg == "result" or model_arg == "results":
        load_data_results(electiondate_arg, live_arg, test_arg, all_arg)
    elif model_arg == "candidate" or model_arg == "candidates":
        load_data_candidates(*params)
    elif model_arg == "all":
        load_data_all(*params)
    elif model_arg == "election": # or model_arg == "elections":
        load_data_elections()
    elif model_arg == "resultmanual":
        load_resultcsv_to_resultmanual(electiondate_arg)
    elif model_arg == "resultcsv2check":
        load_resultcsv_to_resultcheck(electiondate_arg)
    elif model_arg == "resultcsv2race":
        load_resultcsv_to_race(electiondate_arg)
    # elif model_arg == "resultcsv2result":
    #     load_resultcsv_to_result(electiondate_arg)

'''
Functions for ResultStage and ResultCheck
'''

def save_results_csv(electiondate_arg, test_arg):

    ## vars from env
    psql_connection = os.environ["PSQL_CONNECTION"]
    ap_api_key = os.environ["AP_API_KEY"]
    file_path = os.environ["SAVER_PATH"]

    ## other vars
    elex_command = "elex results %s" % (electiondate_arg)
    
    csv_file = file_path + "/tmp/results.csv"
    
    save_test = elex_command + " -t > " + csv_file
    save_non_test = elex_command + " > " + csv_file

    ## make sure the necessary vars are populated
    if not psql_connection:
        message = "Please add the following to ~/.bashrc: export PSQL_CONNECTION=\"<connection info here>\""
        slackbot(message)

    if not ap_api_key:
        message = "Please add the following to ~/.bashrc: export AP_API_KEY=\"<ap api key here>\""
        slackbot(message)

    if not file_path:
        message = "Please add the file path to ~/.bashrc based on current environment."
        slackbot(message)

    ## check if test or not and save
        ## is there a way save a csv via the API?
    if test_arg:
        message = "About to save test result data for %s... \n" % (electiondate_arg)
        slackbot(message)
        
        save_start_time = timezone.localtime(timezone.now())
        call(save_test, shell=True)
        save_end_time = timezone.localtime(timezone.now())

        message = "\nSaved: " + str(csv_file)
        slackbot(message)

        save_length = str(unicode(save_end_time - save_start_time)) 
        message = "Save length:\t\t%s" % (save_length)
        slackbot(message)

    else:
        message = "About to save non-test result data for %s... \n" % (electiondate_arg)
        slackbot(message)
        
        save_start_time = timezone.localtime(timezone.now())
        call(save_non_test, shell=True)
        save_end_time = timezone.localtime(timezone.now())
        
        message = "\nSaved: " + str(csv_file)
        slackbot(message)

        save_length = str(unicode(save_end_time - save_start_time)) 
        message = "Save length:\t\t%s" % (save_length)
        slackbot(message)


def save_json_results_csv(electiondate_arg, test_arg):            

    ## vars from env
    file_path = os.environ["SAVER_PATH"]
    ap_api_key = os.environ["AP_API_KEY"]

    ## files
    json_file = file_path + "/tmp/results.json"
    csv_file = file_path + "/tmp/results.csv"

    today_date = str(timezone.localtime(timezone.now()).date())
    today = int(today_date.replace("-", ""))

    ## figure out which election object to use
    if test_arg:
        election = Election.objects.filter(dataentry="manual", electiondate=electiondate_arg, test=True, testdate=today)
    else:
        election = Election.objects.filter(dataentry="automated", electiondate=electiondate_arg)[0]
    
    ## define which states are related to that election
    election_states = election.state_mm

    ## if there are any states, use those
    if election_states.count() > 0:
        states = list(election_states.iterator())
    ## or else use all the McClatchy states
    else:
        states = ["CA", "FL", "GA", "ID", "IL", "KS", "KY", "MO", "MS", "NC", "PA", "SC", "TX", "WA"]

    state_query_string = ""
    number_of_states = len(list(states))
    state_list = []

    ## add each state to a query string for the JSON data download and set the state list to display in ouput bc iterator() -- as a python generator -- object won't display states
    for state in states:
        # print "State: " + str(state) + "\n"
        state_query = "&statePostal=%s" % (state)
        # print "State query: " + state_query + "\n"
        state_query_string += state_query
        if number_of_states != 14:
            state_list.append(str(state.name))
        else: 
            state_list.append(state)

    message = "Test?\t\t %s\n" % (test_arg)
    slackbot(message)

    start_time = timezone.localtime(timezone.now())
    start_message = '\nStarted data download:\t\t' + str(unicode(start_time))

    message = start_message
    slackbot(message)

    ## construct AP election API url to save
    url = "http://api.ap.org/v2/elections/%s?apiKey=%s&format=json&test=%s%s" % (electiondate_arg, ap_api_key, test_arg, state_query_string)
    # download_command = "curl -o %s %s" % (json_file, url)

    ## grab the contents and write to a file
    response = requests.get(url)
    text = response.text
    with open(json_file, 'wb') as f:
        f.write(text)
    message = "\n\nDownloading JSON from AP for\n" + str(state_list) + "\n"
    slackbot(message)
    # call(download_command, shell=True)

    ## convert json to csv and save as result.csv
    elex_convert_command = "elex results --data-file %s %s > %s" % (json_file, electiondate_arg, csv_file)
    
    message = "\n\nConverting JSON to csv with elex\n\n"
    slackbot(message)
    call(elex_convert_command, shell=True)

    end_time = timezone.localtime(timezone.now())

    end_message = '\nFinished data download:\t' + str(unicode(end_time)) + '\n\n'
    ## QUESTION: Store download_length in db???? 
        # ex: download_length_result or constructed abstracted based on model_arg when var populated
    download_length = str(unicode(end_time - start_time)) 

    message = end_message
    slackbot(message)

    message = 'Data download length:\t\t' + download_length
    slackbot(message)
    message = '--------------------------------------------------'
    slackbot(message)


def load_result_psql(model_arg):
    from django.db import connection
    import psycopg2

    ## vars, somewhat redundant with vars declared in save_results_csv() function
    psql_connection = os.environ["PSQL_CONNECTION"]
    file_path = os.environ["SAVER_PATH"]
    csv_file = file_path + "/tmp/results.csv"

    def model_count(model_arg):
        if model_arg == "resultstage":
            count = str(ResultStage.objects.all().count())
        elif model_arg == "resultcheck":
            count = str(ResultCheck.objects.all().count())
        return count

    ## truncate table
    if model_arg == "resultstage":
        truncate_sql = "\"TRUNCATE TABLE results_resultstage CASCADE;\""
    elif model_arg == "resultcheck":
        truncate_sql = "\"TRUNCATE TABLE results_resultcheck CASCADE;\""
    else:
        message = "No model name match found"
        slackbot(message)
    truncate_command = psql_connection + " " + truncate_sql

    ## ?????????? combine TRUNCATE and COPY commands into one statement? ??????????

    message = "About to remove %s from %s table..." % (model_count(model_arg), model_arg) 
    slackbot(message)
    ## pass this to subprocess
    call(truncate_command, shell=True)
    ## should we use the mgmt cmd instead? is one faster? if so, will need to be refactored to account for ResultCheck
    # from django.core.management import call_command
    # call_command('delete_result_psql', model_arg)

    ## load data via psql copy method
    cursor = connection.cursor()
    ## should it be the way below or this way from a stackoverflow answer?
        # COPY results_resultstage FROM stdin WITH CSV HEADER DELIMITER as ',';
    message = "\nAbout to load..."
    slackbot(message)
    if model_arg == "resultstage":
        copy_sql = '''
                    COPY results_resultstage FROM stdin DELIMITER ',' CSV HEADER;
                    '''
    elif model_arg == "resultcheck":
        copy_sql = '''
                    COPY results_resultcheck FROM stdin DELIMITER ',' CSV HEADER;
                    '''
    with open(csv_file, 'r') as f:
        cursor.copy_expert(sql=copy_sql, file=f)
        connection.commit()
        cursor.close()
    message = "%s loaded:\t%s" % (model_arg, model_count(model_arg)) 
    slackbot(message)


class Command(BaseCommand):
    help = 'Imports for candidates, races and results for automated AP data and manual Google Sheet data.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('model', 
            help='Specify the model (candidate, race, result, resultstage, resultcheck) you want to grab and load'
        )

        parser.add_argument('electiondate', 
            help='Specify the election date as YYYY-MM-DD'
        )
        
        ## named, optional arguments
        parser.add_argument('-l', '--live',
            action='store_true',
            dest='live',
            default=False,
            help='Specify where live is True or False'
        )

        parser.add_argument('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='Specify whether test is True or False'
        )

        parser.add_argument('-a', '--all',
            action='store_true',
            dest='all',
            default=False,
            help='Specify whether to download all data or just defined McClatchy states'
        )

    def handle(self, *args, **options):
        message = "\n"
        slackbot(message)
        
        model_arg = options['model']
        if model_arg == "resultcsv2check":
            message = "Model name: \t\tresultcsv2check"
        elif model_arg == "resultcsv2manual":
            message = "Model name: \t\tresultcsv2manual"
        else:
            message = "Model name: \t\t" + model_arg
        slackbot(message)

        electiondate_arg = options['electiondate']
        message = "Election date: \t\t" + electiondate_arg
        slackbot(message)

        live_arg = options['live']
        message = "Is live? \t\t" + str(live_arg) ## stringified bc it's a boolean
        slackbot(message)

        test_arg = options['test']
        message = "Is test? \t\t" + str(test_arg) ## stringified bc it's a boolean
        slackbot(message)

        all_arg = options['all']
        message = "Download all? \t\t" + str(all_arg) ## stringified bc it's a boolean
        slackbot(message)

        message = "\n"
        slackbot(message)

        def is_not_resultstage_or_resultcheck(model_arg):
            model_arg_length = len(model_arg)
            ## 11 is the length of resultstage and resultcheck
            if model_arg_length != 11:
                return True
            else:
                return False

        if is_not_resultstage_or_resultcheck(model_arg):
            ## delete model(s) for that electiondate to avoid duplicates before re-loading
                ## goal: remove this bc we'll use update instead of delete
            if model_arg != "all":
                delete_filtered(self, model_arg, electiondate_arg)
            else:
                delete_filtered(self, "race", electiondate_arg)
                delete_filtered(self, "result", electiondate_arg)
                delete_filtered(self, "candidate", electiondate_arg)
        elif all_arg:
            ## grab the full results csv via Elex
            save_results_csv(electiondate_arg, test_arg)
        else:
            ## grab the json directly from AP and convert to csv
            save_json_results_csv(electiondate_arg, test_arg)

        ## outputs time info to stdout
        # start_time()
        # start_info(self)
        start_time = timezone.localtime(timezone.now())

        start_message = '\nStarted import:\t\t' + str(unicode(start_time)) + '\n'

        message = start_message
        slackbot(message)

        ## this is where the IMPORTANT FUNCTIONS are called
        if is_not_resultstage_or_resultcheck(model_arg):
            ## function calls for loading Candidate, Race and/or Result
            load_model(electiondate_arg, model_arg, live_arg, test_arg, all_arg)
        else:
            ## function call to load and truncate for ResultStage
            load_result_psql(model_arg)

        ## outputs time info to stdout
        # end_info(self, start_time)
        end_time = timezone.localtime(timezone.now())

        end_message = '\nFinished import:\t' + str(unicode(end_time)) + '\n\n'
        ## QUESTION: Store import_length in db???? 
            # ex: import_length_result or constructed abstracted based on model_arg when var populated
        import_length = str(unicode(end_time - start_time)) 

        message = end_message
        slackbot(message)

        message = 'Import length:\t\t' + import_length
        slackbot(message)
        message = '--------------------------------------------------'
        slackbot(message)

        # bake the api to static for automated and manual results
        # if model_arg == "resultstage":
        #     call_command('bake_api', electiondate_arg, 'resultlive')
        #     call_command('generate_json', electiondate_arg, 'resultlive')
        # elif model_arg == "resultmanual":
        #     call_command('bake_api', electiondate_arg, 'resultmanual')
        #     call_command('generate_json', electiondate_arg, 'resultmanual')

