# from results.models import ResultStage
# from rest_framework import viewsets #, permissions
# from electionsproject.serializers import *


# # ViewSets define the view behavior.
# class CandidateViewSet(viewsets.ModelViewSet):
#     queryset = Candidate.objects.all()
#     serializer_class = CandidateSerializer

# class ElectionViewSet(viewsets.ModelViewSet):
#     queryset = Election.objects.all()
#     serializer_class = ElectionSerializer

# class RaceViewSet(viewsets.ModelViewSet):
#     queryset = Race.objects.all()
#     serializer_class = RaceSerializer

# class ResultLiveViewSet(viewsets.ModelViewSet):
#     queryset = ResultStage.objects.all() # .order_by('-last_updated')
#     serializer_class = ResultLiveSerializer

# class StoryLinkViewSet(viewsets.ModelViewSet):
#     queryset = StoryLink.objects.all()
#     serializer_class = StoryLinkSerializer

# # class UserViewSet(viewsets.ModelViewSet):
# #     queryset = User.objects.all()
# #     serializer_class = UserSerializer
