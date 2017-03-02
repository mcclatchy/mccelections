from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
# from tastypie.authentication import Authentication, ApiKeyAuthentication
# from tastypie.authorization import Authorization
from tastypie.http import HttpApplicationError
from tastypie.resources import *
from results.models import Candidate, Race, Result, ResultManual, Election, ResultStage, ResultPosted#, ResultLive
from electionsproject.settings import mccelectionsenv
import os


class CandidateResource(ModelResource):
    class Meta:
        queryset = Candidate.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        max_limit = None
        filtering = {
            'ballotorder': ALL,
            'candidateid': ALL,
            'created': ALL,
            'dataentry': ALL,
            'datasource': ALL,
            'electiondate': ALL,
            'first': ALL,
            'last': ALL,
            'party': ALL,
            'polid': ALL,
            'polnum': ALL,
            'test': ALL,
            'systemupdated': ALL,
        }

class ElectionResource(ModelResource):
    class Meta:
        queryset = Election.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        max_limit = None
        filtering = {
            'dataentry': ALL,
            'datasource': ALL,
            'description': ALL,
            'electiondate': ALL,
            # 'end_time': ALL,
            # 'live': ALL,
            # 'start_time': ALL,
            'test': ALL,
            'title': ALL,
        }

class RaceResource(ModelResource):
    class Meta:
        queryset = Race.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        max_limit = None
        fields = [
            'dataentry',
            'datasource',
            'electiondate',
            'is_ballot_measure',
            'national',
            'officename',
            'nonpartisan',
            'note',
            'party',
            'raceid',
            'racetype',
            'seatname',
            'seatnum',
            'statepostal',
            'test',
            'uncontested',
            'lastupdated',
            'votingsystem',
        ]
        filtering = {
            'dataentry': ALL,
            'datasource': ALL,
            'electiondate': ALL,
            'is_ballot_measure': ALL,
            'national': ALL,
            'officename': ALL,
            'nonpartisan': ALL,
            'note': ALL,
            'party': ALL,
            'racetype': ALL,
            'raceid': ALL,
            'seatname': ALL,
            'seatnum': ALL,
            'statepostal': ALL,
            'test': ALL,
            'uncontested': ALL,
            'lastupdated': ALL,
            'votingsystem': ALL,
        }

class RaceEmbedResource(ModelResource):
    class Meta:
        queryset = Race.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        max_limit = None
        fields = [
            'dataentry',
            'datasource',
            'electiondate',
            'embed_code',
            # 'embed_code_ap',
            'is_ballot_measure',
            'national',
            'officename',
            'nonpartisan',
            'note',
            'party',
            'raceid',
            'racetype',
            'seatname',
            'seatnum',
            'statepostal',
            'test',
            'uncontested',
            'lastupdated',
            'votingsystem',
        ]
        filtering = {
            'dataentry': ALL,
            'datasource': ALL,
            'electiondate': ALL,
            'embed_code': ALL,
            # 'embed_code_ap': ALL,
            'is_ballot_measure': ALL,
            'national': ALL,
            'officename': ALL,
            'nonpartisan': ALL,
            'note': ALL,
            'party': ALL,
            'racetype': ALL,
            'raceid': ALL,
            'seatname': ALL,
            'seatnum': ALL,
            'statepostal': ALL,
            'test': ALL,
            'uncontested': ALL,
            'lastupdated': ALL,
            'votingsystem': ALL,
        }

class ResultResource(ModelResource):
    class Meta:
        # queryset = Result.objects.all()
        # queryset = Result.objects.exclude(test=True)
        if mccelectionsenv != "prod":
            queryset = Result.objects.all()
        else:
            queryset = Result.objects.exclude(test=True)
        allowed_methods = ['get']
        max_limit = None
        fields = [
            'ballotorder',
            'dataentry',
            # 'description',
            'electiondate',
            'fipscode', 
            'first', 
            'incumbent',
            'is_ballot_measure',
            'last',
            'lastupdated',
            'level',
            'note',
            'officename',
            'national', 
            'party', 
            'precinctsreportingpct',
            'raceid', 
            'racetype',
            'reportingunitname',
            'seatname', 
            'statepostal',
            'test', 
            'votecount',
            'votepct', 
            'winner'
        ]
        include_resource_uri = False
        filtering = {
            'ballotorder': ALL,
            # 'description': ALL,
            'dataentry': ALL,
            'electiondate': ALL,
            'fipscode': ALL,
            'first': ALL,
            'incumbent': ALL,
            'is_ballot_measure': ALL,
            'last': ALL,
            'lastupdated': ALL,
            'level': ALL,
            'national': ALL,
            'note': ALL,
            'officename': ALL, 
            'party': ALL,
            'precinctsreportingpct': ALL,
            'raceid': ALL,
            'racetype': ALL,
            'reportingunitname': ALL,
            'seatname': ALL,
            'statepostal': ALL,
            'test': ALL,
            'votecount': ALL,
            'winner': ALL,
        }

class ResultfullResource(ModelResource):
    class Meta:
        # queryset = Result.objects.all()
        # queryset = Result.objects.exclude(test=True)
        if mccelectionsenv != "prod":
            queryset = Result.objects.all()
        else:
            queryset = Result.objects.exclude(test=True)
        allowed_methods = ['get']
        include_resource_uri = False
        max_limit = None
        filtering = {
            'ballotorder': ALL,
            'candidateid': ALL,
            'created': ALL,
            'dataentry': ALL,
            'datasource': ALL,
            'delegatecount': ALL,
            'description': ALL,
            'election_date': ALL,
            'fipscode': ALL,
            'first': ALL,
            'incumbent': ALL,
            'initialization_data': ALL,
            'is_ballot_measure': ALL,
            'last': ALL,
            'level': ALL,
            'national': ALL,
            'note': ALL,
            'officeid': ALL,
            'officename': ALL,
            'party': ALL,
            'polid': ALL,
            'polnum': ALL,
            'precinctsreporting': ALL,
            'precinctsreportingpct': ALL,
            'precinctstotal': ALL,
            'raceid': ALL,
            'racetype': ALL,
            'racetypeid': ALL,
            'reportingunitid': ALL,
            'reportingunitname': ALL,
            'runoff': ALL,
            'seatname': ALL,
            'seatnum': ALL,
            'statename': ALL,
            'statepostal': ALL,
            'test': ALL,
            'uncontested': ALL,
            'lastupdated': ALL,
            'systemupdated': ALL,
            'votecount': ALL,
            'votepct': ALL,
            'winner': ALL,
        }

class ResultLiveResource(ModelResource): 
    class Meta:
        if mccelectionsenv != "prod":
            queryset = ResultStage.objects.all()#.order_by('statepostal', '-raceid', '-votecount')
        else:
            ## exclude test objects
            queryset = ResultStage.objects.exclude(test=True)
        
        ## future idea for when Stage and Manual inherit/flow into Live:
        # from django.utils import timezone
        # today = str(timezone.localtime(timezone.now()).date())
        # queryset = ResultStage.objects.filter(electiondate=today)

        ## enable in the future? consult with Danny first
            ## it would likely eliminate need for ResultCheck, but wouldn't solve the zero display request they have
        # queryset = ResultStage.objects.filter(precinctsreportingpct__gt=0) 
        allowed_methods = ['get']
        max_limit = None
        fields = [
            'ballotorder',
            # 'description',
            'electiondate',
            'fipscode', 
            'first',
            'incumbent',
            'is_ballot_measure',
            'last', 
            'lastupdated',
            'level',
            'national',
            'officename',
            'party', 
            'precinctsreportingpct',
            'raceid', 
            'racetype',
            'reportingunitname',
            'seatname',
            'statepostal', 
            'test',
            'votecount',
            'votepct', 
            'winner'
        ]
        include_resource_uri = False
        filtering = {
            'ballotorder': ALL,
            # 'description': ALL,
            'electiondate': ALL,
            'fipscode': ALL,
            'first': ALL,
            'incumbent': ALL,
            'is_ballot_measure': ALL,
            'last': ALL,
            'lastupdated': ALL,
            'level': ALL,
            'national': ALL,
            'officename': ALL,
            'party': ALL,
            'precinctsreportingpct': ALL,
            'raceid': ALL,
            'racetype': ALL,
            'reportingunitname': ALL,
            'seatname': ALL,
            'statepostal': ALL,
            'test': ALL,
            'votecount': ALL,
            'votepct': ALL,
            'winner': ALL,
        }


class ResultStageResource(ModelResource): 
    class Meta:
        queryset = ResultStage.objects.all()
        allowed_methods = ['get']
        max_limit = None
        fields = [
            'ballotorder',
            'description',
            'electiondate',
            'fipscode', 
            'first',
            'incumbent',
            'is_ballot_measure',
            'last', 
            'level',
            'national',
            'officename',
            'party', 
            'precinctsreportingpct', 
            'raceid',
            'racetype',
            'reportingunitname',
            'seatname',
            'statepostal', 
            'test',
            'votecount', 
            'winner'
        ]
        include_resource_uri = False
        filtering = {
            'ballotorder': ALL,
            'description': ALL,
            'electiondate': ALL,
            'fipscode': ALL,
            'first': ALL,
            'incumbent': ALL,
            'is_ballot_measure': ALL,
            'last': ALL,
            'level': ALL,
            'national': ALL,
            'officename': ALL,
            'party': ALL,
            'precinctsreportingpct': ALL,
            'raceid': ALL,
            'racetype': ALL,
            'reportingunitname': ALL,
            'seatname': ALL,
            'statepostal': ALL,
            'test': ALL,
            'votecount': ALL,
            'winner': ALL,
        }


class ResultManualResource(ModelResource):
    class Meta:
        # queryset = ResultManual.objects.all()
        # queryset = ResultCsv.objects.all()
        ## exclude test depending on env
        # queryset = ResultManual.objects.exclude(test=True)
        # queryset = ResultLive.objects.exclude(test=True) ## UNCOMMENT THIS to get manual results from gdoc
        if mccelectionsenv != "prod":
            queryset = ResultManual.objects.all()#.order_by('-votecount')
        else:
            queryset = ResultManual.objects.exclude(test=True)#.order_by('-votecount')
        allowed_methods = ['get']
        max_limit = None
        fields = [
            'dataentry',
            'datasource',
            'electiondate',
            'fipscode', 
            'first', 
            'incumbent',
            'is_ballot_measure',
            'last',
            'lastupdated',
            'level', 
            'note',
            'officename',
            'party', 
            'precinctsreporting',
            'precinctsreportingpct',
            'raceid',
            'racetype',
            'reportingunitname',
            'seatname', 
            'statepostal', 
            # 'test',
            'votecount',
            'votepct',
            'winner'
        ]
        include_resource_uri = False
        filtering = {
            'dataentry': ALL,
            'datasource': ALL,
            'description': ALL,
            'electiondate': ALL,
            'fipscode': ALL,
            'first': ALL,
            'incumbent': ALL,
            'is_ballot_measure': ALL,
            'last': ALL,
            'lastupdated': ALL,
            'level': ALL,
            'officename': ALL,
            'note': ALL,
            'party': ALL,
            'precinctsreporting': ALL,
            'precinctsreportingpct': ALL,
            'raceid': ALL,
            'racetype': ALL,
            'reportingunitname': ALL,
            'seatname': ALL,
            'statepostal': ALL,
            # 'test': ALL,
            'votecount': ALL,
            'votepct': ALL,
            'winner': ALL,
        }

class ResultPostedResource(ModelResource):
    class Meta:
        queryset = ResultPosted.objects.all()
        allowed_methods = ['get']
        ## use these after auth enabled
        # allowed_methods = ['get', 'post', 'put']
        max_limit = None
        # authorization = Authorization()
        # authentication = Authentication()
        # authentication = ApiKeyAuthentication()
        fields = [
            'dataentry',
            'datasource',
            'electiondate',
            'fipscode', 
            'first', 
            'id',
            'incumbent',
            'is_ballot_measure',
            'last',
            'level', 
            'note',
            'officename',
            'party', 
            'precinctsreporting',
            'precinctsreportingpct',
            'raceid', 
            'racetype',
            'reportingunitname',
            'seatname', 
            'statepostal', 
            'test',
            'votecount',
            'votepct',
            'winner'
        ]
        include_resource_uri = False
        filtering = {
            'dataentry': ALL,
            'datasource': ALL,
            'description': ALL,
            'electiondate': ALL,
            'fipscode': ALL,
            'first': ALL,
            'id': ALL,
            'incumbent': ALL,
            'is_ballot_measure': ALL,
            'last': ALL,
            'level': ALL,
            'officename': ALL,
            'note': ALL,
            'party': ALL,
            'precinctsreporting': ALL,
            'precinctsreportingpct': ALL,
            'raceid': ALL,
            'racetype': ALL,
            'reportingunitname': ALL,
            'seatname': ALL,
            'statepostal': ALL,
            'test': ALL,
            'votecount': ALL,
            'votepct': ALL,
            'winner': ALL,
        }
