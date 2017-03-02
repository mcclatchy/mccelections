from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.management import call_command
from django.db.models import Sum, Avg
from results.models import Election, ResultStage, ResultCheck
from electionsproject.settings import mccelectionsenv, RESULTSTAGE_IMPORT_SLEEP_TIME
from results.slackbot import slackbot
from shutil import copyfile
import os
import time
import sys


'''
base functions
'''

## return a quersyset of all election objects
def election_objects():
    ## queryset of all Elections
    election_objects = Election.objects.all()
    return election_objects

# return one specific election object based on given date
def election_obj(electiondate_arg):
    elections = election_objects()
    election_id = electiondate_arg.replace("-", "")
    try:
        election_filtered = elections.filter(id=election_id, dataentry="automated")
        election_filtered_obj = election_filtered[0] ## gets the first item
        return election_filtered_obj
    except:
        pass
    try:
        election_filtered = elections.filter(electiondate=electiondate_arg).exclude(dataentry="automated")
        election_filtered_obj = election_filtered[0] ## gets the first item
        return election_filtered_obj
    except:
        pass

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

## create a management command for any of these??? 
    ## besides snapshot, what might be used elsewhere?

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

def snapshot_local(electiondate_string):
    ## for efficiency, we just copy the tmp file for local snapshots instead of saving anew
    ## this is only for local bc otherwise it would fill up the servers
        ## S3 snapshot would be needed for test/prod
    ## should we snapshot manual results from gdoc? use separate parent dir to avoid conflict

    # call_command('snapshot_results')

    ## copy and rename results.csv w/ cp command
    file_path = os.environ["SAVER_PATH"]
    origin = file_path + "/tmp/results.csv"
    now = timezone.localtime(timezone.now())
    save_date = now.date()
    save_date_string = str(save_date)
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')

    snapshot_filename = "results%s.csv" % (timestamp)
    destination_dir = "%s/%s/%s" % (file_path, electiondate_string, save_date_string)
    destination = "%s/%s" % (destination_dir, snapshot_filename)

    message = "\nSNAPSHOTTING\nSaving to the following directory:\n%s\n" % (destination_dir)
    slackbot(message)

    ## making the dir, if it's not there
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    ## copy the file
    copyfile(origin, destination)

    message = "File copied for snapshot\n"
    slackbot(message)


def check_vote_count(election, counter_eval, election_test_today, all=""):
    
    all_arg = str(all)

    message = "\n------------------ CHECK VOTE COUNT ------------------\nChecking %s" % (election)
    slackbot(message)

    electiondate_string = str(election.electiondate)
    ## NEW
    election_test = election.test
    ## OLD
    # try:
    #     election_test = election.test
    #     election_testdate = election_test_today.testdate
    # except:
    #     pass

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
        if all_arg:
            call_command("import_ap_elex", "resultcheck", electiondate_string, test_arg, "-a")
        else:
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
        if all_arg:
            call_command("import_ap_elex", "resultcheck", electiondate_string, "-a")
        else:
            call_command("import_ap_elex", "resultcheck", electiondate_string)

    ## check if there are any votes included in ResultCheck
    ## this returns a dict of the aggregate key and value
    votecount_check = resultcheck_objects().aggregate(Sum("votecount"))
    ## and pulls the value out of the dict
    votecount_total = votecount_check.values()[0]

    if counter_eval != 0:
        ## checks last updated for the most recently updated item
        current_lastupdated = update_check

        ## trying to discern whether election is really "live" and if results are about to start flowing by looking at lastupdated time change, which usually happens after polls close; IMPORTANT to have this bc AP may declare a winner even if no votes have been tabulated yet
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
        ## still not sure lastupdated check will be foolproof, but seems worth trying
    if votecount_total > 0 or election_updated:
        if votecount_total > 0:
            message = "Votes are starting to come in! We'll stop checking and start importing."
            slackbot(message)
            resultstage_import = True
            resultcheck_eval = False
            # return resultstage_import
            # return resultcheck_eval
        if election_updated:
            message = "The election results lastupdated time has changed. We'll stop checking and start importing."
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


def import_resultstage(election_object, election_test_today, counter_import, now, today_string, all=""):

    all_arg = str(all)

    message = "\n--------------- IMPORT RESULTS STAGE ---------------\n %s" % (election_object)
    slackbot(message)

    election = election_object
    electiondate_string = str(election.electiondate)

    if election_test_today:
        if all_arg:
            call_command('import_ap_elex', 'resultstage', electiondate_string, "-t", "-a")
        else:
            call_command('import_ap_elex', 'resultstage', electiondate_string, "-t")
    else:
        if all_arg:
            call_command('import_ap_elex', 'resultstage', electiondate_string, "-a")
        else:
            call_command('import_ap_elex', 'resultstage', electiondate_string)

    ## snapshot
    if mccelectionsenv == "local":
        snapshot_local(electiondate_string)
    # else:
        ## snapshot to S3

    ## this would likely be where we'd bake live results, but that process needs to happen at the end of import_ap_elex mgmt command due to possible later updates run independent of this election_auto script

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
    hours = 12 ## ABSTRACT???

    if election_test_today:
        expiration_length = 60 ## ABSTRACT???
    else:
        expiration_length = 60 * hours

    ## QUESTION: do we want to do this? reduce import frequency if it's been more than XX hours?
    if counter_import == expiration_length:
        timer_expired = True
        ## set sleep time at 5 mins -- extended import time
        sleep_import = 300 ## ABSTRACT???
    else:
        timer_expired = False
        ## set sleep time for 60 seconds
        # sleep_import = 60
        sleep_import = RESULTSTAGE_IMPORT_SLEEP_TIME

    ## returns a dict of the aggregate key and value
    precinctsreportingpct_check = resultstage_objects().aggregate(Avg("precinctsreportingpct"))
    ## pulls the value out of the dict
    precinctsreportingpct_avg = precinctsreportingpct_check.values()[0] * 100

    ## for informational, not logic/check, purposes:
    precinctsreportingpct_avg_state = resultstage_objects().filter(level="state").aggregate(Avg("precinctsreportingpct")).values()[0] * 100
    precinctsreportingpct_avg_state_pres = resultstage_objects().filter(level="state", officename="President").aggregate(Avg("precinctsreportingpct")).values()[0] * 100

    if precinctsreportingpct_avg and precinctsreportingpct_avg_state and precinctsreportingpct_avg_state_pres:
        message = "PERCENT AVERAGES\nPercent avg total:\t\t\t%d \nPercent avg state-level:\t\t%d \nPercent avg state-level for prez:\t%d \n" % (int(precinctsreportingpct_avg), int(precinctsreportingpct_avg_state), int(precinctsreportingpct_avg_state_pres))
        slackbot(message)
    elif precinctsreportingpct_avg_state and precinctsreportingpct_avg:
        message = "PERCENT AVERAGES\nPercent avg total:\t\t\t%d \nPercent avg state-level:\t\t%d" % (int(precinctsreportingpct_avg), int(precinctsreportingpct_avg_state))
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
        message = "\nSetting election live field to False and setting the end time.\n"
        slackbot(message)

        sleep_import = 0

        if not election_test_today:
            last_line = "- the script to sleep long enough to allow for the cache to clear\n"
        else:
            last_line = ""

        message = "\nSet the following...\n - the load loop to stop \n - the \"live\" field for " + electiondate_string + " automated Election to False \n%s - the loop sleep time var to 0 to exit the loop immediately\n\nLoading the archive..." % (last_line)
        slackbot(message)

        ## load archive result data
        if election_test_today:
            if all_arg:
                call_command('import_ap_elex', 'result', electiondate_string, "-t", "-a")
            else:
                call_command('import_ap_elex', 'result', electiondate_string, "-t")
        else:
            if all_arg:
                call_command('import_ap_elex', 'result', electiondate_string, "-a")
            else:
                call_command('import_ap_elex', 'result', electiondate_string)
            message = "\n@channel: The import has completed for the election on %s\n" % (electiondate_string)
            slackbot(message)

        ## if it's not a test, sleep the script so the cache has time to reset with the archive data before clearing resultstage
        # if not election_test_today:
        #     number_of_minutes = 15
        #     archive_cache_time = 60 * number_of_minutes
            # time.sleep(archive_cache_time)
            # message = "Sleeping for:\t%s minutes" % (number_of_minutes)

        ## delete ResultStage data
        clear_resultstage_resultcheck(resultstage_objects(), resultcheck_objects())

        if election_test_today:
            ## all election tests for today
            election_tests = Election.objects.filter(test=True, testdate=today_string)
        else:
            election_tests = 0
            resultstage_import = False

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
        elif election_tests == 1 or election_tests == 0:
            resultstage_import = False
            sys.exit()
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
def loadresults_checkcount(date="", all=""):

    all_arg = str(all)

    master_loop = True

    while master_loop:
        ## current date/time whenever referenced
        now = timezone.localtime(timezone.now()) ## gives actual NY date/time
        ## today's date
        today = now.date()

        ## if the optional date arg is included, override the default
        if date:
            today_string = date
        else:
            today_string = str(today)

        ## election_obj function pulls the zero-indexed value
        election = election_obj(today_string)

        ## is there an election?
        if election:
            election_today = True
        else:
            election_today = False

        ## all election tests for today
        election_tests = Election.objects.filter(test=True, testdate=today_string)

        ## if one or more test elections exist
        if election_tests:
            ## how many?
            election_tests_count = election_tests.count()
            election_test_today = True
        else:
            election_test_today = False

        ## if there's an election or test today...
        if election_today or election_test_today:
            if election_today:
                if election.dataentry == "manual" and not election.url:
                    message = "\nOh, hello! There's a manual election today: "
                    slackbot(message)
                    message = "- " + str(election)
                    slackbot(message)
                ## NEED TO ACCOUNT FOR when there's both an automated + manual/admin, automated + manual/gdoc elections
                # elif election.dataentry == "manual" and election.url:
                #     message = "\nOh, hello! There's a manual gdoc election today: "
                #     slackbot(message)
                #     message = "- " + str(election)
                #     slackbot(message)
                elif election.dataentry == "automated":
                    message = "\nOh, hello! There's an automated election today: "
                    slackbot(message)
                    message = "- " + str(election)
                    slackbot(message)
            ## NEED TO ACCOUNT FOR gdoc election tests
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

            while resultcheck_eval:
                ## non-test election
                if election_today:
                    # ## check vote count and if it returns False, then...
                    # if not check_vote_count(election, counter_eval, election_test_today):
                    #     resultcheck_eval = False
                    #     resultstage_import = True

                    ## uses this form to match the correctly starttime value
                    now = timezone.now()
                    election_starttime = election.starttime

                    ## if there's no starttime or the starttime is less than or equal to now
                    if not election_starttime or election_starttime <= now:
                        message = "\nChecking " + str(election) + "..."
                        slackbot(message)
                        ## check vote count and if it returns False, then...
                        if not check_vote_count(election, counter_eval, election_test_today, all=all_arg):
                            resultcheck_eval = False
                            resultstage_import = True
                    else:
                        message = "\nToday's election has a start time, so we won't check until then:\n%s\n%s GMT\n" % (election, election_starttime)
                        slackbot(message)

                ## test election(s)
                elif election_test_today:
                    from itertools import chain

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
                                if not check_vote_count(election, counter_eval, election_test_today, all=all_arg):
                                    resultcheck_eval = False
                                    resultstage_import = True
                                    break
                            else:
                                message = "\nThe following election has a start time, so we won't check until then:\n%s\n%s GMT\n" % (election, election_starttime)
                                slackbot(message)

                        # ## after looping through the election tests, sleep and keep checking
                        # if resultcheck_eval:
                        #     sleep_eval = 60
                        #     message = "No votes yet. The vote check loop will sleep for %s seconds before checking again.\n\n-------------------------------------------------\n" % (sleep_eval)
                        #     slackbot(message)
                        #     time.sleep(sleep_eval)

                    ## if there are no more election tests
                    elif not election_tests_to_check:
                        message = "\n @channel: Well, that's a wrap. No more election tests for today!\n"
                        slackbot(message)
                        resultcheck_eval = False
                        resultstage_import = False
                        master_loop = False

                ## after looking at the election/election test(s), sleep and keep checking
                if resultcheck_eval:
                    sleep_eval = 60
                    message = "No votes yet. The vote check loop will sleep for %s seconds before checking again.\n\n-------------------------------------------------\n" % (sleep_eval)
                    slackbot(message)
                    time.sleep(sleep_eval)

                ## everything here was moved to the check_vote_count function

            ## resultstage_import loop can only run on a single election (not all elections) specific to a day
            counter_import = 0

            ## while resultstage_import var is True...
            while resultstage_import:

                ## if conditions for continuing to to import to resultstage are False, then stop this loop
                if not import_resultstage(election, election_test_today, counter_import, now, today_string, all=all_arg):
                    resultstage_import = False
                ## or else keep it going
                else:
                    resultstage_import = True

                counter_import += 1
                message = "\nNumber of imports:\t" + str(counter_import)
                slackbot(message)

                ## !! everything here was moved to the import_resultstage function

            ## end of import while loop
        else:
            message = "\nNOTICE: There's no election today!\n"
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

        parser.add_argument('-a', '--all',
            action='store_true',
            dest='all',
            default=False,
            help='Specify whether to download all data or just defined McClatchy states'
        )

    def handle(self, *args, **options):

        ## or should this be called electiondate to be more specific?
        date_arg = options['date']
        if date_arg:
            message = "\nDate override: \t\t" + str(date_arg)
            slackbot(message)

        all_arg = options['all']
        message = "Download all? \t\t" + str(all_arg) ## stringified bc it's a boolean
        slackbot(message)

        loadresults_checkcount(date=date_arg, all=all_arg)

