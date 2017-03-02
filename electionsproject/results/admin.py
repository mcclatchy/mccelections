from django.contrib import admin
# from django.contrib.admin import AdminSite
# from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
# from django.forms.models import ModelForm
from .models import *
## for admin log
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
# from django.core.urlresolvers import reverse
## for nested inlines
# import nested_admin


## code that is supposed to save unchanged or empty inlines
    ## via http://stackoverflow.com/a/3734700/217955
# class AlwaysChangedModelForm(ModelForm):
#     def has_changed(self):
#         """ Should returns True if data differs from initial. 
#         By always returning true even unchanged inlines will get validated and saved."""
#         return True

# class CheckerInline(admin.StackedInline):
#     """ Base class for checker inlines """
#     extra = 0
#     form = AlwaysChangedModelForm

# class MyAdminSite(AdminSite):
#     index_title = ugettext_lazy('McClatchy election result data')


class CandidateAdmin(admin.ModelAdmin):
    fields = ['election_fk', 'first', 'last', 'party_fk', 'is_ballot_measure', 'incumbent', 'test']
    list_display = ['last', 'first', 'party_fk', 'is_ballot_measure', 'incumbent', 'test'] # 
    list_filter = ['party_fk', 'incumbent', 'is_ballot_measure', 'test'] # , 'updated_ap'
    search_fields = ['last', 'first', 'incumbent', 'party_fk__name']

    ## function to override default get_queryset and exclude AP-imported or older manual candidates from the admin
    def get_queryset(self, request):
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=30)
        qs_full = super(CandidateAdmin, self).get_queryset(request)
        qs_excluded = qs_full.exclude(datasource='Associated Press').filter(electiondate__gte=time_offset)
        return qs_excluded 


class DataSourceAdmin(admin.ModelAdmin):
    fields = ['source_name', 'contact_first', 'contact_last', 'contact_title', 'email_address', 'phone_number', 'website']
    list_display = ['source_name', 'contact_first', 'contact_last', 'contact_title', 'email_address', 'phone_number', 'view_website']
    # list_editable = []
    # list_filter = []
    search_fields = ['source_name', 'contact_first', 'contact_last', 'contact_title', 'email_address', 'phone_number', 'website']


class EmbedAdmin(admin.ModelAdmin):
    fields = ['name', 'label', 'election_fk', 'embed_type', 'race_mm', 'view_more_results_link', 'embed_code']
    search_fields = ['name', 'embed_type', 'label']
    list_display = ['name', 'label', 'election_fk', 'embed_type']
    list_filter = ['embed_type', 'election_fk']
    filter_horizontal = ['race_mm']
    readonly_fields = ('embed_code',)


class PartyAdmin(admin.ModelAdmin):
    fields = ['name', 'abbreviation']
    list_display = ['name', 'abbreviation']
    # list_editable = ['']
    # list_filter = ['name']
    search_fields = ['name']
    # exclude  = ['']


# class ResultManualInLine(nested_admin.NestedTabularInline):
class ResultManualInLine(admin.TabularInline):
    model = ResultManual
    # fields = ['candidate_name_fk', 'votecount', 'votepct', 'precinctsreportingpct']
    fields = ['candidate_name_fk', 'reportingunitname', 'race_name_fk', 'statepostal', 'level', 'votecount', 'votepct', 'precinctsreportingpct'] # , 'precinctsreportingpct_formatted', 'votepct_formatted'
    readonly_fields = ('votepct', 'precinctsreportingpct', 'candidate_name_fk', 'reporting_unit_fk', 'race_name_fk', 'reportingunitname', 'statepostal', 'level', )
    show_change_link = True
    extra = 0

    def has_add_permission(self, request):
        return False


# class ReportingUnitInLine(nested_admin.NestedTabularInline):
class ReportingUnitInLine(admin.TabularInline):
    model = ReportingUnit
    fields = ['location_fk', 'race_fk', 'statepostal', 'level', 'precinctstotal', 'precinctsreporting', 'precinctsreportingpct'] ## precinctsreportingpct_formatted
    readonly_fields = ('race_fk', 'precinctsreportingpct', 'location_fk', 'statepostal', 'level',) # 'race_fk',) 
    show_change_link = True
    extra = 0
#     inlines = [ResultManualInLine]

    def has_add_permission(self, request):
        return False


class RaceInLine(admin.TabularInline):
    model = Race
    fields = ['officename_fk', 'seatname_fk', 'statepostal', 'racetype', 'party', 'candidate_mm', 'uncontested', 'national', 'test'] # 'nonpartisan', 'votingsystem', 'live', 
    extra = 0


# class ElectionForm(forms.ModelForm):
#     class Meta:
#         model=Election
#         fields = "__all__" 

#         def validate_url(self):
#             url = self.cleaned_data.get("url")
#             if url:
#                 querystring = "output=csv"
#                 if not querystring in url:
#                     error = "You have entered an incorrect URL. It must end in %s. Please go back to your Google sheet and get the corret URL." % (querystring)
#                     raise forms.ValidationError(error)
#             return self.cleaned_data["url"]


# class ElectionAdmin(nested_admin.NestedModelAdmin):
class ElectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('electiondate', 'title', 'description')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('state_mm', 'test', 'testdate', 'starttime', 'endtime', 'live', 'resultcount', 'url', 'liveresults', 'testresults')
        })
    )
    # fields = ['electiondate', 'title', 'description', 'state_mm', 'test', 'testdate', 'starttime', 'endtime', 'live', 'resultcount', 'url', 'liveresults', 'testresults'] # 'level', ## 'races_mm', # 'reportingunit_mm', 'resultmanual_mm', ## these two mm have been tossed, probably for good (but it would be good to use m2m search/filter to add)
    list_display = ['title', 'electiondate', 'starttime', 'endtime', 'test', 'testdate', 'live'] # , 'description', 'start_time', 'end_time', 'live'
    # list_editable = ['electiondate', 'starttime', 'endtime', 'test', 'testdate', 'live']
    list_filter = ['electiondate', 'testdate', 'test', 'live']
    search_fields = ['title']
    ## do we want this editable in the list view? maybe initially, but probably not long-term
    # list_editable = ['live']
    # inlines = [ReportingUnitInLine] #, ResultManualInLine] ## REQUIRES foreign key to Election model
    inlines = [ReportingUnitInLine, ResultManualInLine]
    # inlines = [RaceInLine] # ReportingUnitInLine, ResultManualInLine, ## these don't work bc they require a foreign key, but that foreign key isn't linked to the other fk
    readonly_fields = ('resultcount', 'liveresults', 'testresults',) # , 'live'
    save_as = True
    filter_horizontal = ['state_mm']

    # form = ElectionForm

    ## make automated Election entries read-only (or at least for the core fields?) for all users or non-admin users

    ## function to override default get_queryset and exclude AP-imported objects from this admin
        ## ideally, we'd like to do this for all non-superusers so admin can still see them
    # def get_queryset(self, request):
    #     qs_full = super(ElectionAdmin, self).get_queryset(request)
    #     qs_excluded = qs_full.exclude(datasource='Associated Press') ## it seems this should really be 
    #     return qs_excluded 


class RaceAdmin(admin.ModelAdmin):
    fields = ['election_fk', 'datasource_fk', 'officename_fk', 'seatname_fk', 'statepostal', 'racetype', 'party_fk', 'candidate_mm', 'note', 'nonpartisan', 'votingsystem', 'uncontested', 'national', 'test', 'embed_code'] #  # 'officename', 'seatname', 'starttime', 'endtime', 'live', 'description',
    list_display = ['officename', 'party_fk', 'racetype', 'is_ballot_measure', 'seatname', 'statepostal', 'electiondate', 'election_electiondate', 'uncontested', 'nonpartisan', 'votingsystem', 'test'] # 'starttime', 'endtime', # 'officename', 'seatname' # 'election_fk', # 'is_ballot_measure', ## i_b_m is redudant bc info is in racetype field
    list_editable = ['nonpartisan']
    list_filter = ['electiondate', 'dataentry', 'national', 'racetype', 'is_ballot_measure', 'party_fk', 'uncontested', 'nonpartisan', 'votingsystem', 'test', 'statepostal', 'officename', 'seatname'] # 'live', 'starttime', 'endtime', 
    ## search fields need to include both self fields and fk'ed fields
    search_fields = ['officename', 'officename_fk__officename', 'party', 'party_fk__name', 'racetype', 'seatname', 'seatname_fk__seatname', 'statepostal', 'test', 'uncontested']
    filter_horizontal = ['candidate_mm']
    readonly_fields = ('embed_code', 'national',)
    actions = ['generate_race_embed_codes']

    ## function to override default get_queryset and exclude AP-imported objects from this admin
    def get_queryset(self, request):
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        qs_full = super(RaceAdmin, self).get_queryset(request)
        qs_excluded = qs_full.filter(electiondate__gte=time_offset)#.exclude(datasource='Associated Press')
        return qs_excluded 

    ## add admin action to generate race embed code list for user
    def generate_race_embed_codes(self, request, queryset):
        message = ""
        for race in queryset:
            message += str(race.embed_code)
            # message.append(race.embed_code)
        self.message_user(request, "%s" % message)
    generate_race_embed_codes.short_description = "Get embed codes for selected races"


class ReportingUnitAdmin(admin.ModelAdmin):
    fields = ['election_fk', 'race_fk', 'location_fk', 'statepostal', 'precinctstotal', 'precinctsreporting', 'precinctsreportingpct_formatted', 'test'] # 'reportingunitname', 'level', 
    list_display = ['reportingunitname', 'statepostal', 'level', 'race_fk', 'electiondate', 'precinctstotal_reformatted', 'precinctsreporting', 'precinctsreportingpct_formatted', 'test'] # 'race_fk', 'reporting_unit_level', 
    list_editable = ['precinctsreporting']
    list_filter = ['electiondate', 'level', 'location_fk', 'statepostal', 'precinctstotal', 'test']
    search_fields = ['reportingunitname', 'location_fk__locationname', 'level', 'statepostal', 'precinctstotal', 'precinctsreportingpct'] # 'reporting_unit_level', 
    readonly_fields = ('precinctsreportingpct_formatted',)

    ## function to override default get_queryset and exclude old reporting units from the admin
    def get_queryset(self, request):
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=30)
        qs_full = super(ReportingUnitAdmin, self).get_queryset(request)
        ## only show reporting units from Elections 7 days ago and going forward
        qs_excluded = qs_full.filter(electiondate__gte=time_offset) 
        return qs_excluded


class ResultAdmin(admin.ModelAdmin):
    fields = ['first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test']
    list_display = ['last', 'first', 'officename', 'seatname', 'electiondate', 'statepostal', 'created', 'lastupdated', 'reportingunitname', 'level', 'party', 'precinctsreportingpct_formatted', 'votecount', 'votepct_formatted', 'winner', 'test'] # 'description', 'reportingunitname', 'is_ballot_measure', 'unique_id',
    # list_editable = [] 
    list_filter = ['created', 'electiondate', 'dataentry', 'level', 'winner', 'test', 'statepostal', 'party', 'officename'] # 'seatname', 'reportingunitname', 'is_ballot_measure',
    search_fields = ['last', 'first', 'officename', 'seatname', 'description', 'statepostal', 'level', 'party', 'reportingunitname']
    readonly_fields = ('first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test',)
    

## can this inherit completely from ResultAdmin?
class ResultLiveAdmin(admin.ModelAdmin):
    fields = ['first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test']
    list_display = ['last', 'first', 'officename', 'seatname', 'electiondate', 'statepostal', 'lastupdated', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test'] # 'description', 'reportingunitname', 'is_ballot_measure', 'unique_id',
    list_editable = ['precinctsreportingpct', 'votecount', 'votepct', 'winner'] # 'officename', 'seatname', 'description', 'statepostal', 'level', 'party', 'reportingunitname', 
    list_filter = ['lastupdated', 'electiondate', 'level', 'party', 'winner', 'test', 'statepostal', 'officename', 'seatname'] # 'reportingunitname', 'is_ballot_measure',
    search_fields = ['last', 'first', 'officename', 'seatname', 'description', 'statepostal', 'level', 'party', 'reportingunitname']


## THESE ARE DISTINCT FROM main RESULT model
class ResultManualAdmin(admin.ModelAdmin):
    ## 'precinctstotal' and 'precinctsreportingpct' now in ReportingUnit model
    fields = ['election_fk', 'datasource_fk', 'race_name_fk', 'candidate_name_fk', 'reporting_unit_fk', 'votecount', 'votepct_formatted', 'national', 'runoff', 'test', 'winner'] # 'votepct_caculated', 'ballot_measure_fk', 'is_ballot_measure' # 'electiondate', 'first', 'last', 'level', 'officename', 'party', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'reportingunitname', 'seatname', 'statepostal', 'votepct' ## <-- those are the fields that are populated in overriden save method; enable if you need to see
    list_display = ['candidate_name_fk_reformatted', 'officename', 'seatname', 'electiondate', 'systemupdated', 'statepostal', 'reportingunitname_reformatted', 'party', 'votecount', 'votepct_formatted', 'precinctsreportingpct_formatted', 'winner', 'test'] # 'race_election_date', 'reportingunit_link', 'race_seat_name', ## 'race_name_fk', 'statepostal', 'votepct', 'office_name_fk', 'seat_name_fk', 'last', 'first', 'description', 'reportingunitname', 'is_ballot_measure', 'unique_id', 
    list_editable = ['votecount', 'winner'] # 'office_name_fk', 'seat_name_fk', 'description', 'statepostal', 'level', 'party', 'reportingunitname', 
    list_filter = ['electiondate', 'systemupdated', 'party', 'statepostal', 'reportingunitname', 'winner', 'test'] # 'race_election_date', 'race_party', 'race_seat_name', 'race_office_name', 'is_ballot_measure', 
    search_fields = ['first', 'last', 'description', 'race_name_fk__party', 'reportingunitname', 'officename', 'seatname', 'party', 'statepostal', 'level'] # 
    readonly_fields = ('votepct_formatted', 'national',) # 'electiondate', 'first', 'last', 'level', 'officename', 'party', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'reportingunitname', 'seatname', 'statepostal', 'votepct' ## <-- those are the fields that are populated in overriden save method; enable if you need to see

    ## function to override default get_queryset and exclude gdoc-imported and old manual results from this admin
    def get_queryset(self, request):
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=30)
        qs_full = super(ResultManualAdmin, self).get_queryset(request)
        ## only show manual results from Elections 7 days ago and going forward, plus exclude results imported from gdoc bc they don't have foreign key relationships needed to display in this admin, thus causing an error when included
        qs_excluded = qs_full.filter(electiondate__gte=time_offset, gdoc_import=False) 
        return qs_excluded


class ResultPostedAdmin(admin.ModelAdmin):
    fields = ['electiondate', 'first', 'last', 'level', 'officename', 'party', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'reportingunitname', 'seatname', 'statepostal', 'votecount', 'votepct', 'national', 'runoff', 'test', 'winner'] # 'votepct_caculated', 'ballot_measure_fk', 'is_ballot_measure' # 'electiondate', 'first', 'last', 'level', 'officename', 'party', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'reportingunitname', 'seatname', 'statepostal', 'votepct' ## <-- those are the fields that are populated in overriden save method; enable if you need to see
    list_display = ['last', 'first', 'electiondate', 'level', 'officename', 'party', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'reportingunitname', 'seatname', 'statepostal', 'votecount', 'votepct', 'winner', 'test'] # 'race_seat_name', ## 'race_name_fk', 'statepostal', 'votepct', 'office_name_fk', 'seat_name_fk', 'last', 'first', 'description', 'reportingunitname', 'is_ballot_measure', 'unique_id', 
    # list_editable = ['votecount', 'winner'] # 'office_name_fk', 'seat_name_fk', 'description', 'statepostal', 'level', 'party', 'reportingunitname', 
    list_filter = ['electiondate', 'systemupdated', 'party', 'winner', 'statepostal', 'test'] # 'race_election_date', 'race_party', 'race_seat_name', 'race_office_name', 'reportingunitname', 'is_ballot_measure', 'statepostal', 
    search_fields = ['candidate_name_fk__last', 'candidate_name_fk__first', 'race_name_fk__officename', 'description', 'race_name_fk__party', 'reporting_unit_fk__location_fk__locationname', 'statepostal'] #, 'level', 
    readonly_fields = ('votepct', 'electiondate', 'first', 'last', 'level', 'officename', 'party', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'reportingunitname', 'seatname', 'statepostal', 'votecount', 'votepct', 'winner', 'national', 'runoff', 'test',) ## <-- those are the fields that are populated in overriden save method; enable if you need to see


## can this inherit completely from ResultAdmin?
class ResultStageAdmin(admin.ModelAdmin):
    fields = ['first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test']
    list_display = ['last', 'first', 'officename', 'seatname', 'electiondate', 'statepostal', 'lastupdated', 'reportingunitname', 'level', 'party', 'precinctsreportingpct_formatted', 'votecount_formatted', 'votepct_formatted', 'is_ballot_measure', 'national', 'test', 'winner'] # 'description', 'reportingunitname', 'unique_id',
    # list_editable = []
    list_filter = ['lastupdated', 'electiondate', 'level', 'national', 'party', 'winner', 'test', 'statepostal', 'is_ballot_measure', 'officename', 'seatname'] # 'reportingunitname', 
    search_fields = ['last', 'first', 'officename', 'seatname', 'description', 'statepostal', 'level', 'party', 'reportingunitname']
    readonly_fields = ('first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test',)


class ResultCheckAdmin(admin.ModelAdmin):
    fields = ['first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test']
    list_display = ['last', 'first', 'officename', 'seatname', 'electiondate', 'statepostal', 'lastupdated', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'is_ballot_measure', 'national', 'test', 'winner'] # 'description', 'reportingunitname', 'unique_id',
    # list_editable = []
    list_filter = ['electiondate', 'level', 'winner', 'test', 'statepostal', 'party', 'officename'] # 'seatname', 'reportingunitname', 'is_ballot_measure',
    search_fields = ['last', 'first', 'officename', 'seatname', 'description', 'statepostal', 'level', 'party', 'reportingunitname']
    readonly_fields = ('first', 'last', 'officename', 'seatname', 'electiondate', 'statepostal', 'reportingunitname', 'level', 'party', 'precinctsreportingpct', 'votecount', 'votepct', 'winner', 'test',)


class ResultCsvAdmin(admin.ModelAdmin):
    fields = ['electiondate', 'lastupdated', 'id', 'last', 'first', 'reportingunitname', 'level', 'racetype', 'officename', 'seatname', 'seatnum', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'votecount', 'votepct', 'winner', 'ballotorder', 'note', 'fipscode', 'incumbent', 'is_ballot_measure', 'nonpartisan', 'party', 'statepostal', 'uncontested', 'votingsystem']
    list_display = ['last', 'first', 'lastupdated', 'reportingunitname', 'level', 'racetype', 'officename', 'seatname', 'seatnum', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'votecount', 'votepct', 'winner', 'electiondate', 'incumbent', 'is_ballot_measure', 'party', 'statepostal', 'uncontested']
    # list_editable = ['']
    list_filter = ['reportingunitname', 'level', 'racetype', 'officename', 'seatname', 'seatnum', 'winner', 'electiondate', 'incumbent', 'is_ballot_measure', 'party', 'statepostal', 'uncontested', 'votingsystem', 'lastupdated']
    search_fields = ['last', 'first', 'reportingunitname', 'level', 'racetype', 'officename', 'seatname', 'seatnum', 'note', 'party', 'statepostal']
    # exclude  = ['']
    readonly_fields = ('id', 'last', 'first', 'reportingunitname', 'level', 'racetype', 'officename', 'seatname', 'seatnum', 'precinctsreporting', 'precinctsreportingpct', 'precinctstotal', 'votecount', 'votepct', 'winner', 'ballotorder', 'note', 'electiondate', 'fipscode', 'incumbent', 'is_ballot_measure', 'nonpartisan', 'party', 'statepostal', 'uncontested', 'votingsystem', 'lastupdated',)


class LocationAdmin(admin.ModelAdmin):
    fields = ['locationname', 'level']
    list_display = ['locationname', 'level']
    # list_editable = ['locationname', 'level']
    list_filter = ['locationname', 'level']
    search_fields = ['locationname', 'level']


class OfficeNameAdmin(admin.ModelAdmin):
    fields = ['officename'] #, 'location_fk']
    list_display = ['officename'] #, 'location_fk']
    # list_editable = ['']
    list_filter = ['officename'] #, 'location_fk']
    search_fields = ['officename'] #, 'location_fk']


class SeatNameAdmin(admin.ModelAdmin):
    fields = ['seatname', 'seatnum']
    list_display = ['seatname', 'seatnum']
    # list_editable = ['']
    list_filter = ['seatname', 'seatnum']
    search_fields = ['seatname', 'seatnum']


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    # readonly_fields = LogEntry._meta.get_all_field_names()
    readonly_fields = ('object_id', 'object_repr', 'action_time', 'user', 'content_type', 'action_flag', 'change_message',) # 'object_link',
    list_filter = ['user', 'content_type', 'action_flag']
    search_fields = ['object_repr', 'change_message', 'user']
    list_display = ['action_time', 'user', 'content_type','action_flag', 'change_message',] # 'object_link',

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    # def object_link(self, obj):
    #     if obj.action_flag == DELETION:
    #         link = escape(obj.object_repr)
    #     else:
    #         ct = obj.content_type
    #         link = u'<a href="%s">%s</a>' % (
    #             reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
    #             escape(obj.object_repr),
    #         )
    #     return link
    # object_link.allow_tags = True
    # object_link.admin_order_field = 'object_repr'
    # object_link.short_description = u'object'
    
    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


## TEMPLATE
class StateAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name']
    # list_editable = ['']
    # list_filter = []
    search_fields = ['name']
    # exclude  = ['']


## TEMPLATE
# class Admin(admin.ModelAdmin):
#     fields = ['']
#     list_display = 
#     # list_editable = ['']
#     list_filter = 
#     search_fields = 
#     # exclude  = ['']

# admin_site = MyAdminSite()
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(Embed, EmbedAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(ReportingUnit, ReportingUnitAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(ResultLive, ResultLiveAdmin)
admin.site.register(ResultManual, ResultManualAdmin)
admin.site.register(ResultPosted, ResultPostedAdmin)
admin.site.register(ResultCsv, ResultCsvAdmin)
admin.site.register(ResultCheck, ResultCheckAdmin)
admin.site.register(ResultStage, ResultStageAdmin)
admin.site.register(OfficeName, OfficeNameAdmin)
admin.site.register(SeatName, SeatNameAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(State, StateAdmin)
## TEMPLATE
# admin.site.register(, )