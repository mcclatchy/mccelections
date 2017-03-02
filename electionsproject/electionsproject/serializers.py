# from results.models import ResultStage
# from rest_framework import serializers

# Serializers define the API representation.

# class CandidateSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Candidate
#         fields = ('created','ballot_order','candidate_id','first','last','party','pol_id','pol_num')

# class ElectionSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Election
#         fields = ('title', 'description', 'election_date', 'start_time', 'end_time', 'test', 'live')

# class RaceSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#        model = Race
#        fields = ('created','description','initialization_data','last_updated','national','office_id','office_name','party','race_id','race_type','race_type_id','seat_name','seat_num','state_name','state_postal','test','uncontested') # 'race_id_date'

# class ResultLiveSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = ResultStage
#         fields = ('ballotorder',
#             'description',
#             'electiondate',
#             'fipscode', 
#             'first',
#             'is_ballot_measure',
#             'last', 
#             'level',
#             'officename',
#             'party', 
#             'precinctsreportingpct', 
#             'racetype',
#             'reportingunitname',
#             'seatname',
#             'statepostal', 
#             'test',
#             'votecount', 
#             'winner'
#         ) # 'race_id_date'

# class StoryLinkSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = StoryLink
#         fields = ('headline', 'description', 'state', 'url')

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ('created','url', 'username', 'email', 'is_staff')
