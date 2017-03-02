from elex.api import Elections
from results.elexconnection import election_connection#, election_date_string #, test
## is this importing of the core models redundant with call in import_ap_elex? 
    # I don't think so bc it's just the delete function that needs it -- not the load function calls
from results.models import Candidate, Race, Result, Election, ResultStage, ResultManual, ResultCsv, ResultCheck #, BallotMeasure, ReportingUnit
from results.slackbot import slackbot
import dateutil.parser
import datetime
from choices import state_fips
import random


## add logic to populate specific fields in certain ways 
    # start_time and end_time flowing up and/or down to/from Election and Race?

## THIS DOESN'T WORK; function calls commented out in load functions below
## convert tz date to datetime object
def datetime_parser(tzstring):
    datetime = dateutil.parser.parse(tzstring)
    return datetime

## abstract the model name
# def load_data_by_model(model_arg, electiondate_arg, live_arg, test_arg):
    # choose mapping

## add functions from top of import_ap_elex here ???


### LOAD BY MODEL

## download elections greater than or equal to today
def load_data_elections():

    ## AP elections
    elections_ap = Elections.get_elections(Elections(), datafile=None)
    elections_length = len(elections_ap)

    ## sort all automated elections by the most recent and return that one
    election_latest_imported_auto = Election.objects.filter(dataentry="automated").order_by("-electiondate")[0]
    election_latest_auto_date_formatted = str(election_latest_imported_auto.electiondate)
    election_latest_auto_date_unformatted = int(election_latest_auto_date_formatted.replace("-", ""))

    counter = 0
    counter_not = 0

    message = "Importing..."
    slackbot(message)

    for election_item in elections_ap:

        election_id = election_item.electiondate.replace("-", "")

        today_formatted = datetime.datetime.now().date()
        today_unformatted = int(str(today_formatted).replace("-", ""))
        
        electiondate_formatted = election_item.electiondate
        electiondate_unformatted = int(election_id)

        ## import anything today or after that
        if electiondate_unformatted > election_latest_auto_date_unformatted:
            election_check = True
        else:
            election_check = False
        
        if election_check:

            election_mapping = {
                'dataentry': 'automated',
                'datasource': 'Associated Press',
                'electiondate': election_item.electiondate,
                'id': election_id,
                'liveresults': election_item.liveresults,
                'title': 'Automated election', ## e.g. extract state names and populate a /-separated string or something; or connect w/ FK like manual races
                'testresults': election_item.testresults,
            }
        
            obj, created = Election.objects.update_or_create(**election_mapping)
            # print obj.electiondate

            counter += 1

        elif not election_check:
            counter_not += 1

    message = "\nLoaded:\t\t\t" + str(counter) + " elections"
    slackbot(message)
    message = "Not loaded:\t\t" + str(counter_not) + " elections"
    slackbot(message)


## download all elections
def load_data_elections_all():

    elections = Elections.get_elections(Elections(), datafile=None)
    counter = 0
    counter_not = 0
    message = "Importing..."
    slackbot(message)

    for election_item in elections:
        election_id = election_item.electiondate.replace("-", "")
        election_mapping = {
            'dataentry': 'automated',
            'datasource': 'Associated Press',
            'electiondate': election_item.electiondate,
            'id': election_id,
            'liveresults': election_item.liveresults,
            'title': 'Automated election', ## e.g. extract state names and populate a /-separated string or something; or connect w/ FK like manual races
            'testresults': election_item.testresults,
        }
        obj, created = Election.objects.update_or_create(**election_mapping)
        # print obj.electiondate
        counter += 1

    message = "\nLoaded:\t\t\t" + str(counter) + " elections"
    slackbot(message)
    message = "Not loaded:\t\t" + str(counter_not) + " elections"
    slackbot(message)


def load_data_candidates(electiondate_arg, live_arg, test_arg):

    candidates = election_connection(electiondate_arg, live_arg, test_arg).candidates
    # candidates = election_connection().candidates

    counter = 0

    ## Candidate
    for candidate_item in candidates:

        import datetime
        # mcc_id = int(str(candidate_item.candidateid) + str(candidate_item.polid))
        electiondate_int = electiondate_arg.replace("-", "")
        # mcc_id = int((electiondate_int) + str(candidate_item.polnum))
        # now = str(datetime.datetime.now()).replace(" ", "").replace("-", "").replace(".", "").replace(":", "")
        now = '{:%H%M%S%f}'.format(datetime.datetime.now())
        mcc_id = int(str(candidate_item.polnum) + now)

        ## map Elex fields to model fields
        candidate_mapping = {
            'dataentry': 'automated',
            'datasource': 'Associated Press',
            'ballotorder': candidate_item.ballotorder,
            'candidateid': candidate_item.candidateid,
            'electiondate': electiondate_arg,
            'id': mcc_id,
            'first': candidate_item.first,
            'last': candidate_item.last,
            'party': candidate_item.party,
            'polid': candidate_item.polid,
            'polnum': candidate_item.polnum,
            'unique_id': candidate_item.unique_id,
        }

        ## if mccelectionid exists, update; else create
        obj, created = Candidate.objects.update_or_create(**candidate_mapping)

        counter += 1

    message = "Loaded:\t\t\t" + str(counter) + " candidates"
    slackbot(message)

def load_data_races(electiondate_arg, live_arg, test_arg):

    races = election_connection(electiondate_arg, live_arg, test_arg).races
    # races = election_connection().races

    counter = 0

    ## Race
    for race_item in races:
        
        ## bc raceid is the same as id
            # https://github.com/newsdev/elex/blob/master/elex/api/models.py#L718
        state = race_item.statepostal
        
        ## use state FIPS to include in ID
        state_id = state_fips[state]

        mcc_id = int(str(race_item.electiondate.replace("-", "")) + str(race_item.id) + str(state_id))

        mcc_unique_id = unicode(race_item.electiondate) + '-' + unicode(race_item.raceid) + '-' + unicode(race_item.statename)

        ## map Elex fields to model fields
        race_mapping = {
            'dataentry': 'automated',
            'datasource': 'Associated Press',
            'description': race_item.description, 
            'electiondate': race_item.electiondate,
            'id': mcc_id,
            'is_ballot_measure': race_item.is_ballot_measure,
            'unique_id': mcc_unique_id,
            'initialization_data': race_item.initialization_data, 
            'national': race_item.national, 
            'officeid': race_item.officeid, 
            'officename': race_item.officename, 
            'party': race_item.party, 
            'raceid': race_item.raceid, 
            'racetype': race_item.racetype, 
            'racetypeid': race_item.racetypeid, 
            'seatname': race_item.seatname, 
            'seatnum': race_item.seatnum, 
            'statename': race_item.statename, 
            'statepostal': race_item.statepostal, 
            'test': race_item.test, 
            'uncontested': race_item.uncontested,
            'lastupdated': race_item.lastupdated
            # 'lastupdated': datetime_parser(race_item.lastupdated)
        }

        ## if mccelectionid exists, update; else create
        obj, created = Race.objects.update_or_create(**race_mapping) 
    
        counter += 1

    message = "Loaded:\t\t\t" + str(counter) + " races"
    slackbot(message)

def load_data_results(electiondate_arg, live_arg, test_arg, all_arg):

    ## load from ResultStage...
    results = ResultStage.objects.filter(electiondate=electiondate_arg)

    ## ...unless for some reason there are none there, then load via Elex
    if all_arg and results.count() == 0:
        results = election_connection(electiondate_arg, live_arg, test_arg).results
    # elif not all_arg and results.count() == 0:
        ## load from json
        # from subprocess import call
        # import json
        # import os

        # file_path = os.environ["SAVER_PATH"]
        # json_file = file_path + "/tmp/results.json"
        # results = json.loads(json_file)

    # mcc_id = unicode(result_item.candidateid) + '-' + unicode(result_item.reportingunitid) + '-' + unicode(result_item.level) 

    result_list = [
        ## this one uses datetime_parser
        Result(
            dataentry="automated",
            datasource="Associated Press",
            ballotorder=result_item.ballotorder,
            candidateid=result_item.candidateid,
            # delegatecount=result_item.delegatecount,
            description=result_item.description,
            electiondate=result_item.electiondate,
            fipscode=result_item.fipscode,
            first=result_item.first,
            # id=mcc_id,
            # unique_id=result_item.unique_id,
            incumbent=result_item.incumbent,
            initialization_data=result_item.initialization_data,
            is_ballot_measure=result_item.is_ballot_measure,
            last=result_item.last,
            level=result_item.level,
            # mccelectionid=mccelectionid_constructor,
            national=result_item.national,
            officeid=result_item.officeid,
            officename=result_item.officename,
            party=result_item.party,
            polid=result_item.polid,
            polnum=result_item.polnum,
            precinctsreporting=result_item.precinctsreporting,
            precinctsreportingpct=result_item.precinctsreportingpct,
            precinctstotal=result_item.precinctstotal,
            raceid=result_item.raceid,
            racetype=result_item.racetype,
            racetypeid=result_item.racetypeid,
            reportingunitid=result_item.reportingunitid,
            reportingunitname=result_item.reportingunitname,
            runoff=result_item.runoff,
            seatname=result_item.seatname,
            seatnum=result_item.seatnum,
            statename=result_item.statename,
            statepostal=result_item.statepostal,
            test=result_item.test,
            uncontested=result_item.uncontested,
            lastupdated=result_item.lastupdated,
            votecount=result_item.votecount,
            votepct=result_item.votepct,
            winner=result_item.winner
        )
        for result_item in results
    ]

    results_length = len(result_list)

    ## bulk create method
    Result.objects.bulk_create(result_list)
    # import pdb; pdb.set_trace()

    message = "Loaded:\t\t\t" + str(results_length) + " results"
    slackbot(message)

def load_resultcsv_to_resultmanual(electiondate_arg):
    
    ## queryset of objects to load
    resultcsv_objects = ResultCsv.objects.filter(electiondate=electiondate_arg)
    # resultcsv_objects = ResultCsv.objects.all()

    counter = 0

    for resultcsv in resultcsv_objects:

        ## include a newsroom-specific ID after statepostal to ensure uniqueness?
        resultcsv_raceid = str(resultcsv.electiondate).replace("-", "") + state_fips[resultcsv.statepostal] + str(resultcsv.raceid)

        resultcsv_mapping = {
            'dataentry': "manual",
            # 'datasource': "",
            'ballotorder': resultcsv.ballotorder,
            # 'description': resultcsv.description,
            'electiondate': resultcsv.electiondate,
            'fipscode': resultcsv.fipscode, 
            'first': resultcsv.first, 
            'gdoc_import': True,
            'id': resultcsv.id,
            'incumbent': resultcsv.incumbent,
            'is_ballot_measure': resultcsv.is_ballot_measure,
            'last': resultcsv.last,
            'lastupdated': resultcsv.lastupdated,
            'level': resultcsv.level, 
            'note': resultcsv.note,
            'officename': resultcsv.officename,
            # 'nonpartisan': resultcsv.nonpartisan, ## needs to be uncommented in Result master model
            'party': resultcsv.party, 
            'precinctsreporting': resultcsv.precinctsreporting,
            'precinctsreportingpct': resultcsv.precinctsreportingpct,
            'precinctstotal': resultcsv.precinctstotal,
            'raceid': resultcsv_raceid,
            'racetype': resultcsv.racetype,
            'reportingunitname': resultcsv.reportingunitname,
            'seatname': resultcsv.seatname,
            'seatnum': resultcsv.seatnum,
            'statepostal': resultcsv.statepostal, 
            # 'test': resultcsv.test, ## this isn't in the gdoc sheet, as of now
            'uncontested': resultcsv.uncontested,
            'votecount': resultcsv.votecount,
            'votepct': resultcsv.votepct,
            # 'votingsystem': result.votingsystem, ## needs to be uncommented in Result master model
            'winner': resultcsv.winner
        }

        ## load/create
        obj, created = ResultManual.objects.update_or_create(**resultcsv_mapping)       

        counter += 1

    message = "\nLoaded:\t\t\t" + str(counter) + " results loaded from ResultCsv to ResultManual"
    slackbot(message)

def load_resultcsv_to_race(electiondate_arg):
    ## filtering on the election date shouldn't be necessary, but it's a data check
    resultcsv_objects = ResultCsv.objects.filter(electiondate=electiondate_arg)
    
    ## determines which field to use for creating races
    distinct_fields = ['raceid']

    ## queryset of objects to load unique by what's in values_list
    resultcsv_objects = resultcsv_objects.order_by(*distinct_fields).distinct(*distinct_fields)

    counter = 0

    for resultcsv in resultcsv_objects:

        ## include a newsroom-specific ID after statepostal to ensure uniqueness?
        resultcsv_raceid = str(resultcsv.electiondate).replace("-", "") + state_fips[resultcsv.statepostal] + str(resultcsv.raceid)

        resultcsv_mapping = {
            'dataentry': "manual",
            # 'datasource': "",
            # 'description': resultcsv.description,
            'electiondate': resultcsv.electiondate,
            'gdoc_import': True,
            'id': resultcsv.id,
            'is_ballot_measure': resultcsv.is_ballot_measure,
            'lastupdated': resultcsv.lastupdated,
            'note': resultcsv.note,
            'officename': resultcsv.officename,
            'nonpartisan': resultcsv.nonpartisan,
            'party': resultcsv.party,
            'raceid': resultcsv_raceid, 
            'racetype': resultcsv.racetype,
            'seatname': resultcsv.seatname,
            'seatnum': resultcsv.seatnum,
            'statepostal': resultcsv.statepostal, 
            # 'test': resultcsv.test, ## this isn't in the gdoc sheet, as of now
            'uncontested': resultcsv.uncontested,
            # 'votingsystem': result.votingsystem, ## needs to be uncommented in Result master model
        }

        ## load/create
        obj, created = Race.objects.update_or_create(**resultcsv_mapping)       

        counter += 1

    message = "\nLoaded:\t\t\t" + str(counter) + " races loaded from ResultCsv to ResultRaces"
    slackbot(message)

def load_resultcsv_to_resultcheck(electiondate_arg):
    
    ## queryset of objects to load
    resultcsv_objects = ResultCsv.objects.filter(electiondate=electiondate_arg)
    # resultcsv_objects = ResultCsv.objects.all()

    counter = 0

    for resultcsv in resultcsv_objects:

        resultcsv_mapping = {
            # 'dataentry': "manual",
            # 'datasource': "",
            'ballotorder': resultcsv.ballotorder,
            # 'description': resultcsv.description,
            'electiondate': resultcsv.electiondate,
            'fipscode': resultcsv.fipscode, 
            'first': resultcsv.first, 
            # 'gdoc_import': True,
            'id': resultcsv.id,
            'incumbent': resultcsv.incumbent,
            'is_ballot_measure': resultcsv.is_ballot_measure,
            'last': resultcsv.last,
            'lastupdated': resultcsv.lastupdated,
            'level': resultcsv.level, 
            'note': resultcsv.note,
            'officename': resultcsv.officename,
            # 'nonpartisan': resultcsv.nonpartisan, ## needs to be uncommented in Result master model
            'party': resultcsv.party, 
            'precinctsreporting': resultcsv.precinctsreporting,
            'precinctsreportingpct': resultcsv.precinctsreportingpct,
            'precinctstotal': resultcsv.precinctstotal,
            'racetype': resultcsv.racetype,
            'reportingunitname': resultcsv.reportingunitname,
            'seatname': resultcsv.seatname,
            'seatnum': resultcsv.seatnum,
            'statepostal': resultcsv.statepostal, 
            # 'test': resultcsv.test, ## this isn't in the gdoc sheet, as of now
            'uncontested': resultcsv.uncontested,
            'votecount': resultcsv.votecount,
            'votepct': resultcsv.votepct,
            # 'votingsystem': result.votingsystem, ## needs to be uncommented in Result master model
            'winner': resultcsv.winner
        }

        ## load/create
        obj, created = ResultCheck.objects.update_or_create(**resultcsv_mapping)       

        counter += 1

    message = "\nLoaded:\t\t\t" + str(counter) + " results loaded from ResultCsv to ResultCheck"
    slackbot(message)


## Get lists of Python objects for each of the core models.
    # these models haven't been finished or activated yet
    # move to elexconnection so they don't get called multiple times when running import_ap_elex_all?
# candidate_reporting_units = election_connection().candidate_reporting_units
## This may be helpful for manual entry, but does it unnecessarily complicate things?


## LOAD ALL MODELS

## calls functions to map fields and update/create on respective models
def load_data_all(electiondate_arg, live_arg, test_arg):
    return load_data_candidates(electiondate_arg, live_arg, test_arg), load_data_races(electiondate_arg, live_arg, test_arg), load_data_results(electiondate_arg, live_arg, test_arg) #, load_data_reportingunits(electiondate_arg, live_arg, test_arg), load_data_ballotmeasures(electiondate_arg, live_arg, test_arg)