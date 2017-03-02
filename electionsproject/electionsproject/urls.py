from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.models import User
## if signal receivers are in a separate file from models, uncomment this
# import receivers
## these three for REST framework
# from results.models import *
# from rest_framework import routers # , serializers, viewsets
# from electionsproject.views import *
## Tastypie
from tastypie.api import Api
from electionsproject.api.resources import CandidateResource, ElectionResource, RaceResource, RaceEmbedResource, ResultResource, ResultfullResource, ResultLiveResource, ResultManualResource, ResultStageResource, ResultPostedResource
# from results.views import RaceAutocomplete


## Tastypie
v1_api = Api(api_name='v1')
v1_api.register(CandidateResource())
v1_api.register(ElectionResource())
v1_api.register(RaceResource())
v1_api.register(RaceEmbedResource())
v1_api.register(ResultResource())
v1_api.register(ResultfullResource())
v1_api.register(ResultLiveResource())
v1_api.register(ResultManualResource())
v1_api.register(ResultStageResource())
v1_api.register(ResultPostedResource())

## REST framework: Routers provide an easy way of automatically determining the URL conf.
    # remove the s at the end of each so switch from Tastypie can be seamless?
# router = routers.DefaultRouter()
# router.register(r'candidate', CandidateViewSet)
# router.register(r'election', ElectionViewSet)
# router.register(r'race', RaceViewSet)
# router.register(r'resultlive', ResultLiveViewSet)
# router.register(r'user', UserViewSet)

urlpatterns = [
    # url(r'^race-autocomplete/$', RaceAutocomplete.as_view(), name='race-autocomplete'),
    # url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', admin.site.urls),
    ## Tastypie
    url(r'^api/', include(v1_api.urls)),
    ## Nested admin
    # url(r'^_nested_admin/', include('nested_admin.urls')),
    ## Tasytpie Swagger
    # url(r'api/docs/',
    #   include('tastypie_swagger.urls', namespace='myapi_tastypie_swagger'),
    #   kwargs={
    #       "tastypie_api_module":"myapp.registration.my_api",
    #       "namespace":"myapi_tastypie_swagger",
    #       "version": "0.1"}
    # ),
    ## REST framework: connect the API to use automatic URL routing
    # url(r'^api/v1/', include(router.urls)),
    ## include login URLs for the browsable API
    ## REST framework: 
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ## Swagger docs
    # url(r'^docs/', include('rest_framework_swagger.urls')),
    ## leave commented out
    # url(r'^results/', include('results.urls'))
]