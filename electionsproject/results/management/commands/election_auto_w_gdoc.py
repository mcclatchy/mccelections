"""
beginnings of support for gdoc manual election automation
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.management import call_command
from django.db.models import Sum, Avg
from itertools import chain
from results.models import Election, ResultStage, ResultCheck
from electionsproject.settings import mccelectionsenv
from results.slackbot import slackbot
import time


'''
base functions
'''

# ## return a quersyset of all election objects
# def election_objects():
#     ## queryset of all Elections
#     election_objects = Election.objects.all()
#     return election_objects

# # return one specific election object based on given date
# def election_obj(electiondate_arg):
#     elections = election_objects()
#     election_id = electiondate_arg.replace("-", "")
#     try:
#         election_filtered = elections.filter(id=election_id, dataentry="automated")
#         election_filtered_obj = election_filtered[0] ## gets the first item
#         return election_filtered_obj
#     except:
#         pass
#     try:
#         election_filtered = elections.filter(electiondate=electiondate_arg).exclude(dataentry="automated")
#         election_filtered_obj = election_filtered[0] ## gets the first item
#         return election_filtered_obj
#     except:
#         pass



## return a quersyset of all ResultStage objects
def resultstage_objects():
    resultstage_objects = ResultStage.objects.all()
    return resultstage_objects

## return a count of ResultStage objects
def resultstage_count(resultstage_objects):
    resultstage_count = resultstage_objects.count()
    return resultstage_count

## return a quersyset of all ResultCheck objects
def resultcheck_objects():
    resultcheck_objects = ResultCheck.objects.all()
    return resultcheck_objects

## return a count of ResultCheck objects
def resultcheck_count(resultcheck_objects):
    resultcheck_count = resultcheck_objects.count()
    return resultcheck_count


'''
main functions
'''

## to be called on each following import
def check_resultstage_count_change(electiondate_arg, resultstage_count, election_obj):
    election_obj_resultcount = election_obj.resultcount
    ## if current count is less than initial count
    if resultcheck_count < election_obj_resultcount:
        return True
    else: 
        return False

## create a management command for any of these (minus the vars, which would be imported to each)???

def clear_resultstage_resultcheck(resultstage_objects, resultcheck_objects):
    ## delete ResultStage data
    resultstage_count = resultstage_objects.count()
    resultstage_objects.delete()
    message = "ResultStage items deleted:\t%s" % (resultstage_count)
    slackbot(message)

    ## delete ResultCheck data
    resultcheck_count = resultcheck_objects.count()
    resultcheck_objects.delete()
    message = "ResultCheck items deleted:\t%s" % (resultcheck_count)
    slackbot(message)

def snapshot(electiondate_string):
    ## *** need to have this on S3 or other external location to not fill up server ***
        ## NOTE: instead of saving anew, just use/copy the tmp file?
        ## should we snapshot manual results from gdoc? use separate parent dir to avoid conflict
    if mccelectionsenv == "local":
        # call_command('snapshot_results')
        ## copy and rename results.csv w/ cp command
        file_path = os.environ["SAVER_PATH"]
        orgin = file_path + "/tmp/results.csv"
        now = timezone.localtime(timezone.now())
        save_date = now.date()
        save_date_string = str(save_date)
        timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        
        snapshot_filename = "results%s.csv" % (timestamp)
        destination_dir = "%s/%s/%s" % (file_path, electiondate_string, save_date_string)
        destination = "%s/%s" % (destination_dir, snapshot_filename)
        
        mkdir = "mkdir -p %s" % (destination_dir)
        snapshot = "cp %s %s" % (origin, destination)
        
        ## making the dir, if it's not there
        call(mkdir, shell=True)
        message = "Making new directory, if needed:\n%s" % (destination_dir)
        slackbot(message)
        ## actual snapshot executed
        call(snapshot, shell=True)
        message = "Snapshotting"
        slackbot(message)
    # else:
        # snapshot to S3


def check_vote_count(election, counter_eval, election_test_today):
    message = "\n------------------ CHECK VOTE COUNT ------------------\nChecking %s" % (election)
    slackbot(message)

    electiondate_string = str(election.electiondate)
    try:
        election_test = election.test
        election_testdate = election_test_today.testdate
    except:
        pass

    if counter_eval != 0:
        update_check = resultcheck_objects().order_by('-lastupdated')[0].lastupdated

        ## checks lastupdated for the most recently updated item
        previous_lastupdated = update_check

    ## if it's a test, set the var to be a test flag in the mgmt command
    test_arg = ""
    if election_test:            
        # message = "\nIt's a test!\n"
        # slackbot(message)
        test_arg = "-t"
        ## load ResultCheck test
        call_command("import_ap_elex", "resultcheck", electiondate_string, test_arg)
        ## set/assign the count to Election model
        resultcheck_count_int = resultcheck_count(resultcheck_objects())
        election.resultcount = resultcheck_count_int
        election.save()
        count = str(resultcheck_count_int)
        message = "\nSet result count field on Election model using ResultCheck: %s\n" % (count) 
        slackbot(message)
    else:
        # message = "\nThis is not a test! This is the real thing!\n"
        # slackbot(message)
        ## load ResultCheck non-test
        if not election.url:
            call_command("import_ap_elex", "resultcheck", electiondate_string)
        elif election.url:
            from results.election_loaders import load_resultcsv_to_resultcheck
            ## load from gdoc to ResultCsv
            call_command("csv_import", electiondate_string)
            ## load from ResultCsv to ResultCheck 
            call_command("import_ap_elex", "resultcsv2check", electiondate_string)

            # import pdb; pdb.set_trace()
            ## NOTE: Why can't we just load from gdoc to ResultCheck for this part???? bc the data needs to be in the system; ResultCheck is loaded via psql fields for ResultStage, so we'd need to make gdoc reflect ResultStage, which doesn't work bc we need additional fields (e.g. voting system, nonpartisan) for manual races


    ## check if there are any votes included in ResultCheck
    ## this returns a dict of the aggregate key and value
    votecount_check = resultcheck_objects().aggregate(Sum("votecount"))
    ## and pulls the value out of the dict
    votecount_total = votecount_check.values()[0]

    if counter_eval != 0:
        ## checks last updated for the most recently updated item
        current_lastupdated = update_check

        ## trying to discern whether election is really "live" and if results are about to start flowing by looking at lastupdated time change, which usually happens after polls close
            # e.g. on 3/26 results updated around 2 p.m., but did results start flowing soon thereafter? do we even care if not?
        def election_updated(current_lastupdated, previous_lastupdated):
            ## side note: generally, results are loaded with zeroes between midnight and 2 or 3 a.m. ET
            if current_lastupdated > previous_lastupdated:
                return True
            else:
                return False

        election_updated = election_updated(current_lastupdated, previous_lastupdated)

    else:
        election_updated = False

    ## Possible complication with election_updated, from AP:
        ## On Election Day from 1-2 p.m. Eastern, there will be a "live" (non-test) transmission of reports with zeros sent to AP Exchange and Webfeeds; at which time, the test disclaimer in the reports will be removed.
    ## if votes are flowing or lastupdated changed, set end this loop and start the next loop
        ## *** still not sure lastupdated check will be foolproof, but seems worth trying ***
    if votecount_total > 0 or election_updated:
        if votecount_total > 0:
            message = "Votes are starting to come in! We'll stop checking and start importing."
            slackbot(message)
            resultstage_import = True
            resultcheck_eval = False            
            # return resultstage_import
            # return resultcheck_eval
        if election_updated:
            message = "The election data lastupdated time have changed. We'll stop checking and start importing."
            slackbot(message)
            resultstage_import = True
            resultcheck_eval = False
            # return resultstage_import
            # return resultcheck_eval
    else:
        resultstage_import = False
        resultcheck_eval = True
        # return resultstage_import
        # return resultcheck_eval
    # print "\nWHAT IS IT IN THE CHECK LOOP?????\n" + str(resultcheck_eval)
    return resultcheck_eval

    ## everything to return
    # check_vote_values = {}
    # check_vote_values["resultcheck_eval"] = resultcheck_eval
    # # check_vote_values["sleep_eval"] = sleep_eval
    # check_vote_values["resultstage_import"] = resultstage_import
    # return check_vote_values


def import_resultstage(election_object, election_test_today, counter_import, now, today_string):
    message = "\n--------------- IMPORT RESULTS STAGE ---------------\n %s" % (election_object)
    slackbot(message)

    election = election_object
    electiondate_string = str(election.electiondate)
    # print electiondate_string

    if election_test_today:
        test_arg = "-t"
    else:
        test_arg = ""

    ## load ResultStage
    call_command('import_ap_elex', 'resultstage', electiondate_string, test_arg)
    ## snapshot
    # snapshot(electiondate_string)

    # import pdb; pdb.set_trace()

    ## if this loop is the first import, set the resultcount var on the related Election object
    if counter_import == 0:
        ## set resultcheck, get the count and print it
        resultstage_count_int = resultstage_count(resultstage_objects())
        election.resultcount = resultstage_count_int
        election.save()
        count = str(resultstage_count_int)
        message = "\nSet result count field on Election model using ResultStage: %s" % (count) 
        slackbot(message)
        
        ## set the election to live and set that as the start time
        election.live = True
        election.starttime = timezone.localtime(timezone.now())
        election.save()
        message = "Set election to live and set start time\n"
        slackbot(message)

    resultcount_changed = check_resultstage_count_change(electiondate_string, resultstage_count(resultstage_objects()), election)

    ## for the timer
    hours = 12

    if election_test_today:
        expiration_length = 60
    else:
        expiration_length = 60 * hours

    ## QUESTION: do we want to do this? reduce import frequency if it's been more than XX hours?
    if counter_import == expiration_length:
        timer_expired = True
        ## set sleep time at 5 mins -- extended import time
        sleep_import = 300
    else:
        timer_expired = False
        ## set sleep time for 1 min -- standard import time
        sleep_import = 60

    ## returns a dict of the aggregate key and value
    precinctsreportingpct_check = resultstage_objects().aggregate(Avg("precinctsreportingpct"))
    ## pulls the value out of the dict
    precinctsreportingpct_avg = precinctsreportingpct_check.values()[0]

    ## for informational, not logic/check, purposes:
    precinctsreportingpct_avg_state = resultstage_objects().filter(level="state").aggregate(Avg("precinctsreportingpct")).values()[0]
    precinctsreportingpct_avg_state_pres = resultstage_objects().filter(level="state", officename="President").aggregate(Avg("precinctsreportingpct")).values()[0]

    message = "Percent avg total:\t\t\t%d \nPercent avg state-level:\t\t%d \nPercent avg state-level for prez:\t%d \n" % (precinctsreportingpct_avg, precinctsreportingpct_avg_state, precinctsreportingpct_avg_state_pres)
    slackbot(message)

    ## if it's a test, set the % check as president avg
    if election_test_today:
        percent_check = precinctsreportingpct_avg_state_pres
    ## or else set it as overall % avg
    else:
        percent_check = precinctsreportingpct_avg

    ## if the following are true...
        ## there are fewer result objects now than there were initially
        ## the timer is expired
        ## the precincts reporting % avg is 100%      
    if resultcount_changed or timer_expired or percent_check == 100:    
        message = "\n----------------- IMPORT LOOP TERMINATION ------------------\n"
        slackbot(message)
        
        if resultcount_changed:
            message = "Why is it ending?\tResult count changed"
            slackbot(message)
        elif timer_expired:
            message = "Why is it ending?\tTimer expired"
            slackbot(message)
        elif precinctsreportingpct_avg:
            message = "Why is it ending?\tAll precincts reporting"
            slackbot(message)

        ## set the election "live" field as false and the end time
        election.live = False
        election.endtime = timezone.localtime(timezone.now())
        election.save()
        message = "Setting election live field to False and setting the end time.\n"
        slackbot(message)
        
        sleep_import = 0
        
        if not election_test_today:
            last_line = "- the script to sleep long enough to allow for the cache to clear\n"
        else:
            last_line = ""
        
        message = "\nSet the following...\n \
                    - the load loop to stop \n \
                    - the \"live\" field for " + electiondate_string + " automated Election to False \n%s \
                    - the loop sleep time var to 0 to exit the loop immediately\n \
                    Loading the archive...\n" % (last_line)
        slackbot(message)

        ## load archive result data
        call_command('import_ap_elex', 'result', electiondate_string, test_arg)
        
        ## if it's not a test, sleep the script so the cache has time to reset with the archive data before clearing resultstage
        if not election_test_today:
            archive_cache_time = 60 * 15
            time.sleep(archive_cache_time)

        ## delete ResultStage data
        clear_resultstage_resultcheck(resultstage_objects(), resultcheck_objects())
        
        if election_test_today:
            ## all election tests for today
            election_tests = Election.objects.filter(test=True, testdate=today_string)

        ## this restarts the resultcheck loop if there's more than one test
        if election_tests > 1:
            message = "\nOh, hello! There's another test election today: "
            slackbot(message)
            message = election_test_today
            slackbot(message)
            message = "Restarting the resultcheck loop..."
            slackbot(message)
            resultstage_import = False ## this needs to be False bc we need to exit this loop and restart the check loop
            # resultcheck_eval = True
        ## this stops the import loop
        elif election_tests == 1:
            resultstage_import = False
    else:
        resultstage_import = True

    if sleep_import > 0:
        message = "Sleeping the import loop for %s seconds" % (sleep_import)
        slackbot(message)
        time.sleep(sleep_import)

    return resultstage_import

'''
function to call under mgmt cmd handle
'''

# def loadresults_checkcount(electiondate=""):
def loadresults_checkcount(date=""):
    
    master_loop = True

    while master_loop:
        ## current date/time whenever referenced
        # now = timezone.now() ## this gives GMT date/time
        now = timezone.localtime(timezone.now()) ## this gives actual NY date/time
        ## today's date
        today = now.date()

        ## if the optional date arg is included, override the default
        if date:
            today_string = date
        else:
            today_string = str(today)

        ## election_obj function pulls the zero-indexed value
        # election = election_obj(today_string)

        ## queryset of all non-test Elections today
        elections = Election.objects.filter(electiondate=today_string).exclude(test=True)

        ## if there are any non-test Election today
        if elections:
            election_today = True
            election_test_today = False

            ## non-test elections
            elections_automated = elections.filter(dataentry="automated")
            elections_manual_gdoc = elections.exclude(dataentry="automated", url__isnull=True)

            ## variations to account for...
            ## one auto election and no manual_gdoc elections
            if elections_automated.count() == 1 and elections_manual_gdoc.count() == 0:
                election_set = election = elections_automated[0] ## gets the first item
            ## no auto elections + one manual gdoc election
            elif elections_automated.count() == 0 and elections_manual_gdoc.count() == 1:
                election_set = election = elections_manual_gdoc[0]
            ## one auto election + one manual gdoc election
            elif elections_automated.count() == 1 and elections_manual_gdoc.count() == 1:
                election_set = elections_manual_and_gdoc = list(chain(elections_automated, elections_manual_gdoc))

            ## we don't need to account for 
                # one auto election + multiple manual gdoc elections (not possible based on current setup)
                # multiple manual admin elections (doesn't need to be accounted for in this script)

        ## if there aren't any non-test elections
        else:
            election_today = False
        
            ## all election tests for today
            election_tests = Election.objects.filter(test=True, testdate=today_string)
            
            ## if one or more test elections exist
            if election_tests:
                ## how many?
                election_tests_count = election_tests.count()
                election_test_today = True

        ## if there's an election or test today...
        if election_today or election_test_today:
            if election_today:
                if elections_manual_and_gdoc:
                    message = "\nOh, hello! There are automated and manual gdoc elections today: "
                    slackbot(message)
                    for election_obj in elections_manual_and_gdoc:
                        message = "- " + str(election_obj)
                        slackbot(message)
                    # import pdb; pdb.set_trace()
                elif election:
                    if election.dataentry == "manual" and not election.url:
                        message = "\nOh, hello! There's a manual admin election today: "
                        slackbot(message)
                        message = "- " + str(election)
                        slackbot(message)
                    elif election.dataentry == "manual" and election.url:
                        message = "\nOh, hello! There's a manual gdoc election today: "
                        slackbot(message)
                        message = "- " + str(election)
                        slackbot(message)
                    elif election.dataentry == "automated" and not election.url:
                        message = "\nOh, hello! There's an automated election today: "
                        slackbot(message)
                        message = "- " + str(election)
                        slackbot(message)
            ## do we need to account for gdoc election tests?
            elif election_tests_count == 1:
                election = election_tests[0]
                message = "\nOh, hello! There's a test election today: "
                slackbot(message)
                message = "- " + str(election)
                slackbot(message)
            elif election_tests_count > 1:
                message = "\nOh, hello! There are multiple test elections today: "
                slackbot(message)
                for election in election_tests:
                    message = "- " + str(election)
                    slackbot(message)
            resultcheck_eval = True
            counter_eval = 0
            # import pdb; pdb.set_trace()

            while resultcheck_eval:
                def no_votes_yet(resultcheck_eval):
                    ## after looping through the election tests, sleep and keep checking
                    if resultcheck_eval:
                        sleep_eval = 60
                        message = "No votes yet. The vote check loop will sleep for %s seconds before checking again.\n\n-------------------------------------------------\n" % (sleep_eval)
                        slackbot(message)
                        time.sleep(sleep_eval)

                ## non-test election
                if election_today:
                    for election in election_set:
                        ## check vote count and if it returns False, then...
                        if not check_vote_count(election, counter_eval, election_test_today):
                            resultcheck_eval = False
                            if election.url:
                                resultstage_import = False
                                resultmanual_import = True
                            else:
                                resultstage_import = True
                            break

                    ## after looping through the election tests, sleep and keep checking
                    no_votes_yet(resultcheck_eval)
                    # if resultcheck_eval:
                    #     sleep_eval = 60
                    #     message = "No votes yet. The vote check loop will sleep for %s seconds before checking again.\n\n-------------------------------------------------\n" % (sleep_eval)
                    #     slackbot(message)
                    #     time.sleep(sleep_eval)

                ## test election(s)
                elif election_test_today:

                    ## determine and set scope of what to loop thru; i.e. remaining election tests
                    endtime_null = election_tests.filter(endtime__isnull=True) # starttime__isnull=True can't go here bc it might filter out something that started, but never finished and had to be restarted
                    # print "\nNo endtime:\t\t\t" + str(endtime_null)
                    endtime_gt_now = election_tests.filter(endtime__gt=now)
                    # print "\nEndtime_gt_now:\t\t\t" + str(endtime_gt_now)
                    remaining_election_tests = list(chain(endtime_null, endtime_gt_now))
                    # print "\nremaining_election_tests:\t" + str(remaining_election_tests)
                    election_tests_to_check = len(remaining_election_tests)
                    message = "\nHow many remaining test elections today?\n" + str(election_tests_to_check) + "\n" #+ str(remaining_election_tests)
                    slackbot(message)

                    # if there's more than one test election on this day 
                    if election_tests_to_check > 0:                
                        if election_tests_to_check > 1:
                            message = "\nBecause there are multiple election tests, we need to check each of them individually."
                            slackbot(message)
                        
                        ## if any exist, loop thru remaining election tests on this day
                        for election in remaining_election_tests:
                            ## uses this form to match the correctly starttime value
                            now = timezone.now()
                            election_starttime = election.starttime

                            ## if there's no starttime or the starttime is less than or equal to now
                            if not election_starttime or election_starttime <= now:
                                message = "\nChecking " + str(election) + "..."
                                slackbot(message)
                                ## check vote count and see what it returns
                                if not check_vote_count(election, counter_eval, election_test_today):
                                    resultcheck_eval = False
                                    resultstage_import = True
                                    break
                            else:
                                message = "\nThe following election has a start time, so we won't check until then:\n%s\n%s GMT\n" % (election, election_starttime)
                                slackbot(message)

                        ## after looping through the election tests, sleep and keep checking
                        no_votes_yet(resultcheck_eval)
                        # if resultcheck_eval:
                        #     sleep_eval = 60
                        #     message = "No votes yet. The vote check loop will sleep for %s seconds before checking again.\n\n-------------------------------------------------\n" % (sleep_eval)
                        #     slackbot(message)
                        #     time.sleep(sleep_eval)

                    ## if there are no more election tests
                    elif not election_tests_to_check:
                        message = "\nWell, that's a wrap. No more election tests for today!\n"
                        slackbot(message)
                        resultcheck_eval = False
                        resultstage_import = False
                        master_loop = False

                ## !! everything here was moved to the check_vote_count function
           
            ## resultstage_import loop can only run on a single election (not all elections) specific to a day
            counter_import = 0

            ## while resultstage_import var is True...
            while resultstage_import:
                
                # print "Checking which election"
                # print election
                ## if conditions for continuing to to import to resultstage are False, then stop this loop
                if not import_resultstage(election, election_test_today, counter_import, now, today_string):
                    resultstage_import = False
                ## or else keep it going
                else:
                    resultstage_import = True

                counter_import += 1
                message = "Number of imports:\t" + str(counter_import)
                slackbot(message)

                ## !! everything here was moved to the import_resultstage function

            ## end of resultstage_import while loop

            while resultmanual_import:
                
                message = "\n---------- ResultCsv import to ResultManual ------------"
                slackbot(message)
                call_command("import_ap_elex", "resultmanual", today_string)

                counter_import += 1
                message = "Number of imports:\t" + str(counter_import)
                slackbot(message)

        else:
            message = "\nNOTICE: There's no election today! We'll check again tomorrow.\n"
            slackbot(message)
            master_loop = False
    ## end of master_loop

class Command(BaseCommand):
    help = 'Live election procedures to check, load and archive results.'

    def add_arguments(self, parser):
        ## named, optional arguments
        parser.add_argument('-d', '--date',
            # action='store_true',
            type=str,
            dest='date',
            # default=False,
            help='Specify the date as YYYY-MM-DD'
        )

        # parser.add_argument('-e', '--electiondate',
        #     action='store_true',
        #     dest='electiondate',
        #     # default=False,
        #     help='Specify the election date as YYYY-MM-DD'
        # )

    def handle(self, *args, **options):   

        date_arg = options['date']
        if date_arg:
            message = "\nDate override: \t\t" + str(date_arg)
            slackbot(message)

        # electiondate_arg = options['electiondate']
        # message = "Election date: \t\t" + electiondate_arg
        # slackbot(message)

        # loadresults_checkcount(electiondate=electiondate_arg)
        loadresults_checkcount(date=date_arg)
