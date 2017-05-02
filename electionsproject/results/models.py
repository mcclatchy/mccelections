from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.management import call_command
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from results.choices import *
# from results.signals import calculate_vote
from django.db.models.signals import post_save 
from django.dispatch import receiver
from results.calculations import calculated_percent
from electionsproject.settings import mccelectionsenv, RESULTSTABLEJS_EMBED_BASE_URL, AP_EMBED_BASE_URL, SITE_ID


## MODELS

class BasicInfo(models.Model):
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    systemupdated = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name="Updated in system", help_text="This is when the item was updated in the system.") 

    class Meta:
        abstract = True


class DataSource(BasicInfo):
    contact_first = models.CharField(max_length=255, null=True, blank=True, verbose_name="Contact first name", help_text="For point of contact.")
    contact_last = models.CharField(max_length=255, null=True, blank=True, verbose_name="Contact last name", help_text="For point of contact.")
    contact_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Contact title", help_text="For point of contact.")
    # location_fk = models.ForeignKey(Location, null=True, verbose_name="Location")
    email_address = models.EmailField(max_length=254, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True, help_text="Including area code and following this format: ###-###-####")
    source_name = models.CharField(max_length=255, null=True, help_text="Agency, department or organization name.")
    website = models.URLField(max_length=200, null=True, blank=True, help_text="Agency or organization website.")

    def view_website(self):
        return format_html("<a href='{url}' target='_blank'>{site}</a>", url=self.website, site=self.source_name)

        view_website.short_description = self.source_name
        view_website.allow_tags = True
    
    def __unicode__(self):
        return "%s" % (self.source_name)

    class Meta:
        verbose_name = "STEP 1: Data source"


class CommonInfo(BasicInfo):
    dataentry = models.CharField(choices=DATA_ENTRY_CHOICES, default="manual", max_length=255, null=True, verbose_name="Data entry")
    datasource = models.CharField(max_length=255, null=True, blank=True, verbose_name="Data source (via Django import script)")
    datasource_fk = models.ForeignKey(DataSource, null=True, verbose_name="Data source")
    ## if we use newsroom, each model will need it to be added to save method and, ideally, have it pull from the email field
    # newsroom = models.CharField(NEWSROOM_CHOICES, null=True, blank=True)
    test = models.BooleanField(blank=True, default=False)

    ## add/update save method override on respective models -- but not here! -- to update datasource_fk from datasource, which is -- as of Feb 16 -- populated via import_ap_elex mgmt commands

    class Meta:
        abstract = True


## do we need this ???
## delegate could be a field on candidate if candidates could be tied together across states bc they currently repeat across states
# class Delegate(CommonInfo):
    # field
    # field
    # field
    # field


# class FipsCode(BasicInfo):
#     fipscode = models.CharField(max_length=255, null=True) ## needs to be charfield bc of leading zeroes
#     level ## probably should bc there are state and county FIPS


class Location(BasicInfo):
    ## fipscode should probably FK to a model for ease; or M2M so we can use the field to search?
        ## use fipscode field to populate location name on save
    # fipscode_fk = models.ForeignKey(FipsCode)
    # fipscode = models.CharField(choices=FIPS_CHOICES, null=True, verbose_name="Location name")
    locationname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Location name")
    level = models.CharField(choices=LEVEL_CHOICES, max_length=255, null=True, verbose_name="Location level")
    ## if we do this, we'll need to set the choices as a dynamically updating two-tuple of locations
    # locationparent = models.CharField(choices=XXXXXX, max_length=255, null=True, blank=True, verbose_name="Location parent", help_text="What location ")

    # def save(self, *args, **kwargs):
    #     if self.fipscode:        
    #         self.locationname = self.get_fipscode_display()
    #     return super(Location, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s - %s" % (self.locationname, self.level)

    class Meta:      
        verbose_name = "STEP 2: Location"



class OfficeName(BasicInfo):
    # election_fk = models.ForeignKey(Election, verbose_name="Election")
    # location_fk = models.ForeignKey(Location, default="", verbose_name="Location")
    officename = models.CharField(max_length=255, null=True, blank=False, verbose_name="Office name", help_text="e.g. Macon Mayor, Ada County Commissioner, Fresno County Sheriff. Note: If you're using an office name that someone else entered, NEVER update it. If you need something different, then add a new one.")

    class Meta:
        verbose_name = "STEP 3: Office or Ballot Measure name"

    def __unicode__(self):
        # return "%s - %s" % (self.officename, self.location_fk)
        return "%s" % (self.officename)


class SeatName(BasicInfo):
    seatname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat name", help_text="e.g. District 1, Ward 3, etc.")
    seatnum = models.PositiveIntegerField(null=True, blank=True, verbose_name="Seat number", help_text="If there's a number included in the Seat Name, please also enter it here.")
    
    def __unicode__(self):
        return "%s" % (self.seatname)

    class Meta:
        verbose_name = "STEP 4: Seat name (if applicable)"
        verbose_name_plural = "STEP 4: Seat names (if applicable)"


class State(BasicInfo):
    name = models.CharField(choices=STATE_POSTAL_CHOICES, max_length=3, null=False, blank=False)

    def __unicode__(self):
        return "%s" % (self.name)

    class Meta:
        ordering = ['name']


## Election is superset of Race; thus, one or more Races comprise an Election
class Election(CommonInfo):
    """
    Canonical representation of an election on
    a single date and, when applicable, in a single state, 
    including one or more races.
    """
    description = models.TextField(blank=True, null=True, verbose_name="Notes", help_text='Please add all relevant details about the election as needed.')
    ## electiondate can't be PK bc there will be multiples bc of tests
    electiondate = models.DateField(null=True, verbose_name="Election date")
    ## end_time is DateTimeField bc end time could be after midnight
    endtime = models.DateTimeField(null=True, blank=True, verbose_name="End time", help_text="For results, not voting. Can be for test or real election. NOTE: All times must be ET.")
    ## should we include an import_date field for the tests? or just associate one Election test with multiple Race tests?
    # id = models.Autofield(primary_key=True)
    # import_date = models.DateField(null=True)
    live = models.BooleanField(blank=True, default=False, help_text="Is the election result reporting active right now?")
    liveresults = models.BooleanField(blank=True, default=False, verbose_name="Live results?", help_text="From AP via Elex. These indicate there are results, not that the results are \"live\" and flowing.")
    ## resultcount from ResultCheck
    resultcount = models.IntegerField(null=True, blank=True, verbose_name="Number of results", help_text="Calculated automatically on election day or test day.")
    ## make an inline: this shouldn't be here -- ResultManual should inherit the election date via the Race selected
    # resultmanual_mm = models.ManyToManyField(ResultManual, blank=True)
    ## should it pull in states via races?
    state_mm = models.ManyToManyField(State, blank=True, verbose_name="States included", help_text="Select the states included in this election. If none are selected, data for all McClatchy states will be downloaded and imported.")
    starttime = models.DateTimeField(null=True, blank=True, verbose_name="Start time", help_text="For results, not voting. Can be for test or real election. NOTE: All times must be ET.")
    ## would require "choose multiple" options, which means new model with ManyToManyField
    # state = models.CharField(choices=STATE_POSTAL_CHOICES, max_length=255)
    ## test comes from CommonInfo
    testresults = models.BooleanField(blank=True, default=False, verbose_name="Test results?", help_text="From AP via Elex. Appears equivalent to \"test\" field")
    testdate = models.DateField(null=True, blank=True, verbose_name="Test date", help_text="Only enter this if for a test. Also, make sure you check the \"test\" box.")
    title = models.CharField(max_length=255, null=True, help_text="An election is unique by date, includes one or more races and, when applicable, is unique to a single state. The title should concisely include the place, type and year, such as: Idaho primary 2016") 
    url = models.URLField(max_length=255, null=True, blank=True, verbose_name="Google doc URL", help_text="If you're importing this election from a Google spreadsheet, add the URL here. It must include the following at the end of the URL: output=csv")

    ## raise an error if end time is not greater than start time; raise warning if endtime not filled out?

    def save(self, *args, **kwargs):
        ## is this even necessary? maybe. if we ingest AP cal, then that's what would have AP as datasource
        if self.datasource != "Associated Press":
            try:
                 self.datasource = self.datasource_fk.source_name
            except:
                pass
        
        ## construct title based on automated/manual, test/non-test, date?
        # middle_text = "election %s on " % (self.test)
        # self.title = self.dataentry.capitalize() + middle_text + self.electiondate
        ## if a test date is set, set test boolean to True in case it wasn't already
        ## save all related objects from the inlines or just associated reportingunits and resultmanual
        # code would go here: for reportingunit in reportingunits / for result in resultmanual
        if self.testdate:
            self.test = True
        return super(Election, self).save(*args, **kwargs) 


    def __unicode__(self):
        ## switch to just using title if all relevant info is there (date, auto/manual, test/not)
        return "%s on %s" % (self.title, self.electiondate)
        ## idea: return a string that constructs the name based on state, race_type (include multiples?) and year
        # return "%s on %s. Live? %s. Test? %s." % (self.title, self.electiondate, self.live, self.test)

    class Meta:
        ordering = ['-electiondate']
        verbose_name = "STEP 0: Election"


class Party(BasicInfo):
    name = models.CharField(max_length=255, verbose_name="Party name")
    abbreviation = models.CharField(max_length=5, null=True, blank=True, verbose_name="Party abbreviation", help_text="Only add if it's applicable and obvious. For example: D, R, L, I, etc.")

    def __unicode__(self):
        if self.abbreviation:
            display_name = "%s (%s)" % (self.name, self.abbreviation)
        else:
            display_name = "%s" % (self.name)
        return display_name

    class Meta:
        verbose_name_plural = "Parties"


class Candidate(CommonInfo):
    """
    Canonical representation of a
    candidate. Should be globally unique
    for this election, across races.
    """
        # candidate ID not unique across races or states in AP data (e.g. Iowa & NH primary tests on 1/25/16)
        # create a unique ID field based on candidate_id and ???
    ballotorder = models.IntegerField(null=True, blank=True)
    id = models.BigIntegerField(primary_key=True)
    is_ballot_measure = models.BooleanField(default=False, verbose_name="For a ballot measure?", help_text="Check this box if the \"candidate\" you are adding is an option for a ballot measure (e.g. Yes or No as last name).")
    candidateid = models.CharField(max_length=255, null=True, blank=True)
    ## add a delegate field here? if I don't fix so candidates are universally unique, then that logic would need to be written by API users; delegate should be float with two decimal places, per https://github.com/newsdev/elex-admin/issues/18 
    electiondate = models.DateField(null=True, blank=True, verbose_name="Election date") 
    election_fk = models.ForeignKey(Election, null=True, verbose_name="Election", help_text="An election is a superset of races and ballot measures.")
    first = models.CharField(max_length=255, null=True, blank=True, verbose_name="First name", help_text="If it's a ballot measure, leave this blank. The title of the ballot measure is added as part of the \"Office name or Ballot Measure name\" object in the system.")
    incumbent = models.BooleanField(default=False)
    last = models.CharField(max_length=255, null=True, verbose_name="Last name or Ballot Measure response", help_text="If for a ballot measure, enter one of the options (e.g. Yes, No, etc.) as the last name.")
    ## should we use location_fk or race_fk? since you could have two John Smiths in a county, race might be better; but race is defined *after* candidates or else you get into a chicken-and-egg problem
    # location_fk = models.ForeignKey(Location, null=True, verbose_name="Location", help_text="Select a location to be sure candidates are specific to a location")
    party = models.CharField(choices=PARTY_CHOICES, max_length=255, null=True, blank=True, help_text="Leave blank for non-partisan races or for ballot measures. Otherwise, this is required for manual results.")
    party_fk = models.ForeignKey(Party, null=True, blank=True, verbose_name="Party", help_text="Leave blank for non-partisan races or for ballot measures. Otherwise, this is required for manual results.")
    polid = models.CharField(max_length=255, null=True, blank=True)
    polnum = models.CharField(max_length=255, null=True, blank=True)
    # race_mm = models.ManyToManyField(Race, blank=True, verbose_name="Races")
    unique_id = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            import random
            self.id = random.randint(100000000,999999999)
        if self.dataentry != "automated":
            self.dataentry = "manual"
        if self.datasource != "Associated Press":
            try:
                 self.datasource = self.datasource_fk.source_name ## datasource_fk field NOT exposed in admin, so it won't work
            except:
                pass
        if self.election_fk:
            try:
                self.electiondate = self.election_fk.electiondate
            except:
                pass
        try:
            if self.party_fk:
                self.party = self.party_fk.name
        except:
            pass
        ## try to make backward compatible as well?
        return super(Candidate, self).save(*args, **kwargs) 

    def __unicode__(self):
        return "%s %s" % (self.first, self.last)
        # return "%s %s, %s" % (self.first, self.last, self.party)
    
    class Meta:
        verbose_name = "STEP 5: Candidate name or Ballot Measure option"
        ## use instead of unique=True on id_elex in CommonInfo class? is this the most unique way to go?
        # unique_together = ('candidateid', 'last') 


class Race(CommonInfo):
    ## functions to limit what is visible in the admin
    def limit_candidate_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"dataentry": "manual", "electiondate__gte": time_offset}

    def limit_election_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"electiondate__gte": time_offset}

    candidate_mm = models.ManyToManyField(Candidate, blank=True, verbose_name="Candidates", help_text="Double-click a name (or select a name or names and use the arrows) to add or remove candidates.", limit_choices_to=limit_candidate_choices)
    description = models.TextField(null=True, blank=True, help_text="If you selected \"Ballot Issue,\" please enter the text of the issue here if it's short. If not, please add a brief summary.")
    electiondate = models.DateField(null=True, blank=True, verbose_name="Election date")
    election_fk = models.ForeignKey(Election, null=True, verbose_name="Election", help_text="An election is a superset of races and ballot measures.", limit_choices_to=limit_election_choices)
    embed_code = models.TextField(null=True, blank=True, verbose_name="Embed code", help_text="Copy the entire code snippet above (including the < > angle brackets), then paste it into NewsGate using an mm_link or paste directly in Escenic's code view.")
    embed_code_ap = models.TextField(null=True, blank=True, verbose_name="AP embed code", help_text="Copy the entire code snippet above (including the < > angle brackets), then paste it into NewsGate using an mm_link or paste directly in Escenic's code view.")
    gdoc_import = models.BooleanField(default=False, verbose_name="gdoc import?")
    ## ! finish and uncomment import_frequency; use DurationField?
        # https://docs.djangoproject.com/es/1.9/ref/models/fields/#durationfield
    id = models.BigIntegerField(primary_key=True)
    # import_frequency = models.CharField(choices=FREQUENCY_CHOICES, blank=True, help_text="per minute")
    initialization_data = models.BooleanField(default=False)
    is_ballot_measure = models.BooleanField(default=False, blank=True, verbose_name="Ballot measure", help_text="Check this box if the race is a ballot measure, referendum, initiative, recall, etc.")
    endtime = models.DateTimeField(blank=True, null=True, verbose_name="End time", help_text="For results, not voting. All times must be ET and in 24-hour format.")
    ## we shouldn't have a level on here bc races could include multiple levels; altho it could be helpful for filtering, that should really be done on the reportingunit model
    # level = models.CharField(choices=LEVEL_CHOICES, max_length=255, null=True)
    ## live was moved to Election; if it returns here, should be updated like starttime and endtime from Election
    # live = models.BooleanField(blank=True, default=False, help_text="Is the race's result reporting active right now?")
    location_fk = models.ForeignKey(Location, null=True, verbose_name="Location")
    national = models.BooleanField(default=False)
    nonpartisan = models.CharField(choices=NON_PARTISAN_CHOICES, max_length=255, null=True, blank=True, verbose_name="Non-partisan?", help_text="Required for manual entry of local races. Choose 'yes' if there's no party affiliation for the candidates and 'no' if there is.")
    note = models.CharField(max_length=255, null=True, blank=True, help_text="Add short note here if explanation of results needed (e.g. \"Requires a 2/3 majority\", \"Will go to a run-off if no one receives a majority\", etc.)")
    officeid = models.CharField(max_length=255, null=True, blank=True)
    officename_fk = models.ForeignKey(OfficeName, null=True, verbose_name="Office or Ballot Issue name", help_text="e.g. President, Governor, Senator, Representative, Mayor, Councilperson, etc. If there's a location, such as Mayor of Macon, then just add or choose Mayor here and Macon in the Seat Name field.")
    officename = models.CharField(max_length=255, null=True, blank=True, verbose_name="Office or ballot measure name")
    ## only in a primary is party applicable
    party = models.CharField(choices=PARTY_CHOICES, max_length=255, null=True, blank=True, help_text="Only choose a party if it's a primary or caucus.")
    party_fk = models.ForeignKey(Party, null=True, blank=True, verbose_name="Party", help_text="Only choose a party if it's a primary or caucus.")
    raceid = models.CharField(max_length=255, null=True)
    racetype = models.CharField(choices=RACE_TYPE_CHOICES, max_length=255, null=True, verbose_name="Race Type or Ballot Issue", help_text="Choose \"Ballot Issue\" for any if this is measure, initiative, referendum, etc.")
    racetypeid = models.CharField(max_length=255, null=True, blank=True, verbose_name="Race type ID")
    seatname_fk = models.ForeignKey(SeatName, null=True, blank=True, verbose_name="Seat name", help_text="e.g. District 1, Ward 3, etc.")
    seatname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat name")
    seatnum = models.CharField(max_length=255, null=True, blank=True)
    ## hide state_name and, for manual, update it based on statepostal?
    starttime = models.DateTimeField(blank=True, null=True, verbose_name="Start time", help_text="For results, not voting. All times must be ET and in 24-hour format.")
    statename = models.CharField(choices=STATE_CHOICES, max_length=255, null=True)
    statepostal = models.CharField(choices=STATE_POSTAL_CHOICES, max_length=2, null=True, verbose_name="State")
    # test = models.BooleanField(default=False)
    uncontested = models.BooleanField(default=False)
    unique_id = models.CharField(max_length=255, null=True, blank=True)
    lastupdated = models.DateTimeField(null=True, blank=True, verbose_name="Last updated", help_text="This is when the item was last updated.")
    votingsystem = models.CharField(choices=VOTING_SYSTEM_CHOICES, max_length=255, null=True, blank=True, verbose_name="Voting system", help_text="Required for manual entry of local races.")

    ## should this model inherit start/end times and "live" status from Election model? would require Election being scoped to state and date

    def save(self, *args, **kwargs):
        import random
        from choices import state_fips

        if not self.id:
            self.id = random.randint(100000000,999999999)
        ## this seems better
        if not self.dataentry:
            self.dataentry = "manual"
        ## than this
        # if self.dataentry == None:
        #     self.dataentry = "manual"
        ## this
        if self.datasource != "Associated Press":
            try:
                 self.datasource = self.datasource_fk.source_name
            except:
                pass
        ## seems better than this
        # if self.datasource != "Associated Press":
        #     self.datasource = self.datasource_fk.source_name
        try:
            self.electiondate = self.election_fk.electiondate
        except:
            pass
        try:
            if self.party_fk:
                self.party = self.party_fk.name
        except:
            pass
        ## try to make backward compatible as well?
        # try:
        #     if self.party and not self.party_fk:
        #         self.party_fk
        # except:
        #     pass
        ## if there's no race ID (e.g. bc it's manual), construct one
        if not self.raceid:
            constructed_id = str(self.electiondate).replace("-", "") + state_fips[self.statepostal] + str(random.randint(1000,9999))
            self.raceid = int(constructed_id)
        try:
            self.officename = self.officename_fk.officename
        except:
            pass
        try:
            self.seatname = self.seatname_fk.seatname
        except:
            pass
        try:
            self.seatnum = self.seatname_fk.seatnum
        except:
            pass
        base_url = RESULTSTABLEJS_EMBED_BASE_URL
        ## QUERY STRING start with state postal
        query_string = "raceid=%s" % (self.raceid)
        ## replace & with url-encoded version
        query_string = query_string.replace("&", "%26")
        race_name = self
        ## constructing for ResultsTable.js embed: ? for query string included here so it's not replaced above
        self.embed_code = '<!-- %s --><script src="%s?%s"> */ X */ </script>' % (race_name, base_url, query_string)
        ## constructing for API url test
        # self.embed_code = '<script src="%s?format=json%s"> */ X */ </script>' % (base_url, query_string)
        ## AP EMBED CONSTRUCTOR
        ## attempting to abstract, but how much? year? section? race type?
        self.embed_code_ap = '<hr></hr><script language="JavaScript" src="%s%s_%s.js?SITE=%s&SECTION=POLITICS' % (AP_EMBED_BASE_URL, self.statepostal, self.raceid, SITE_ID)
        return super(Race, self).save(*args, **kwargs)

    def is_national(self):
        if self.national:
            return "National"

    def election_electiondate(self):
        if self.election_fk:
            election = self.election_fk
            electiondate = election.electiondate
            election_url = "/admin/results/election/%d/change" % (election.id)
            return format_html("<a href='{url}'>{date}</a>", url=election_url, date=electiondate)
    election_electiondate.short_description = "Election"

    def __unicode__(self):
        name_string_raw = "%s / %s / %s / %s / %s / %s" % (self.statepostal, self.racetype, self.electiondate, self.officename, self.seatname, self.party)
        name_string_fixed = name_string_raw.replace("/ None", "")
        return name_string_fixed

    class Meta:
        ordering = ['-election_fk']
        verbose_name = "STEP 6: Race or Ballot Measure"
        ## activate this so we can use updating instead of deleting everything when we want to refresh?
        # unique_together = ('statepostal', 'raceid')

    # def election_date_string(self):        
    #     return '%s' % self.electiondate


## all fields exist in other models, so this is good for foreign keying
class ReportingUnit(CommonInfo):
    ## function to limit what is visible in the admin
    def limit_race_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"dataentry": "manual", "electiondate__gte": time_offset}

    ## election_fk was removed bc it now pulls that info from the race_fk, but then added back and not exposed bc of a resultmanual error on test server
    election_fk = models.ForeignKey(Election, null=True, verbose_name="Election", help_text="An election is a superset of races, reporting units and ballot measures.")
    electiondate = models.DateField(null=True, verbose_name="Election date")
    level = models.CharField(choices=LEVEL_CHOICES, max_length=255, null=True)
    location_fk = models.ForeignKey(Location, null=True, verbose_name="Reporting unit name", help_text="Choose or add a location.")
    ## listed under Race model
    # statename = models.CharField(max_length=255, null=True, verbose_name="State name")
    statepostal = models.CharField(choices=STATE_POSTAL_CHOICES, max_length=2, null=True, verbose_name="State")
    ## listed under Result model
    # lastupdated = models.CharField(max_length=255, null=True, verbose_name="Last updated", help_text="This is when the item was last updated.")
    precinctsreporting = models.IntegerField(null=True, blank=True, verbose_name="# of precincts reporting", help_text="In this reporting unit.")
    ## in elex, "votepct uses normal form (0.3 for 30%) but precinctsreportingpct multiples by 100 (30 for 30%)"
        ## issue filed by Eads https://github.com/newsdev/elex/issues/204
    precinctsreportingpct = models.DecimalField(max_digits=20, decimal_places=3, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name="% of precincts reporting", help_text="In this reporting unit.")
    precinctstotal = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], null=True, blank=True, verbose_name="Total number of precincts", help_text="In this reporting unit.")
    race_fk = models.ForeignKey(Race, null=True, verbose_name="Race", limit_choices_to=limit_race_choices)
    reportingunitname = models.CharField(max_length=255, null=True, verbose_name="Reporting unit name", help_text="Name of county, township, etc.") 
    ## QUESTION: Do we just want to include...
    ## populate reportingunitname from location_fk.location_name via the overriden save method?
    ## if reportingunitname is the name of the state, then it's somewhat redundant bc we have statepostal field, which to users looks like statename
        ## would we want to mark that as blank=True and then adjust save method to populate reportingunitname with statename if level=="State"?
        ## extend this functionality to city/town/county if they're part of a Location class?
    
    ## need to do this so a name appears
    def election_race_date(self):
        return election_fk.race
    election_race_date.short_description = "Election"

    def location_location_name(self):
        return self.location_fk.location_name
    location_location_name.short_description = "Location"

    def race_name(self):
        race = self.race_fk
        race_url = "/admin/results/race/%d/change" % (race.id)
        return format_html("<a href='{url}'>{title}</a>", url=race_url, title=race)
    # race_name.admin_order_field = "race_fk"
    race_name.short_description = "Race"

    def precinctsreportingpct_formatted(self):
        if self.precinctsreportingpct:
            reformatted_precinctsreportingpct = str(int(round(self.precinctsreportingpct))) + '%'
        else:
            reformatted_precinctsreportingpct = None 
        return reformatted_precinctsreportingpct
    precinctsreportingpct_formatted.admin_order_field = 'precinctsreportingpct'
    precinctsreportingpct_formatted.short_description = format_html('Precincts <br>reporting %')

    def precinctstotal_reformatted(self):
        return self.precinctstotal
    precinctstotal_reformatted.admin_order_field = 'precinctstotal'
    precinctstotal_reformatted.short_description = 'Total precincts'

    # def election_name(self):
    #     election = self.election_fk
    #     election_url = "/admin/results/election/%d/change" % (election.id)
    #     return format_html("<a href='{url}'>{date}</a>", url=election_url, date=election)
    # election_name.short_description = "Election"

    # def local_statepostal(self):
    #     return self.location.
    # precinctsreportingpct_label = format_html("Precincts<br> reporting %")
    # reportingunit_precinctsreportingpct.short_description = precinctsreportingpct_label

    ## uses calculated_percent function
    def save(self, *args, **kwargs):
        if self.location_fk:
            self.reportingunitname = self.location_fk.locationname
            self.level = self.location_fk.level
            ## this would eliminate one user step, but would first require establishing location hierachy to hide the state field in the reporting unit admin; i.e. if you chose a non-state, it would getting populated bc there's not relationship between lower level geographies and a state, as of now
            # if self.location_fk.level == "State":
                # self.statepostal = self.locationname
        if self.precinctsreporting:        
            self.precinctsreportingpct = calculated_percent(self.precinctsreporting, self.precinctstotal)
        elif self.precinctsreporting == None:
            self.precinctsreportingpct = None
        # if self.election_fk:
        #     self.electiondate = self.election_fk.electiondate
        if self.race_fk:
            self.electiondate = self.race_fk.election_fk.electiondate
            self.raceid = self.race_fk.raceid
        return super(ReportingUnit, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s for %s" % (self.location_fk, self.race_fk)

    class Meta:
        verbose_name = "STEP 7: Reporting Unit"


## Result is the master model
    ## ResultManual --> ResultLive --> Result
class Result(CommonInfo):
    unique_id = models.CharField(max_length=255, null=True, blank=True)
    ballotorder = models.IntegerField(null=True, blank=True, verbose_name="Ballot order", help_text="Ballot order of this candidate or issue. For AP data, there may be gaps in sequence.")
    ## foreign key candidate_id to Candidate model?
    candidateid = models.CharField(max_length=255, null=True, verbose_name="Candidate ID")
    # delegatecount = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    electiondate = models.DateField(null=True, verbose_name="Election date")
    ## electiondate doesn't need to FK to Election bc Result is a subset of Race, which is connected to Election
    fipscode = models.CharField(max_length=255, null=True)
    first = models.CharField(max_length=255, null=True, blank=True, verbose_name="Candidate first name")
    ## adding this would require commenting out in ResultManual to deconflict/de-dupe
    # gdoc_import = models.BooleanField(default=False, verbose_name="gdoc import?")
    incumbent = models.NullBooleanField(default=False)
    initialization_data = models.BooleanField(default=False)
    ## how to use if we add ballot measure class?
        ## elex now calls this is_ballot_position
    is_ballot_measure = models.NullBooleanField(default=False, verbose_name="Ballot measure")
    last = models.CharField(max_length=255, null=True, blank=True, verbose_name="Candidate last name")
    lastupdated = models.DateTimeField(null=True, blank=True, verbose_name="Last updated", help_text="This is when the item was last updated.")
    ## FK to a Level model so users can add new ones???
    level = models.CharField(choices=LEVEL_CHOICES, max_length=255, null=True, verbose_name="Reporting unit level")
    national = models.BooleanField(default=False)
    note = models.CharField(max_length=255, null=True, blank=True)
    ## if nonpartisan is activated, be sure to activate in election_loaders for ResultCsv to ResultManual function
        # also, be sure to update ResultManual save method so the value in Race populates the comparable value
    # nonpartisan = models.CharField(max_length=255, null=True, blank=True, verbose_name="Non-partisan?")
    ## office_id list in AP docs pg 33-34; use elex mapping; hide in the admin? how to handle for office_name values hand-keyed by users? if front-end dev expects, it'll be empty
    officeid = models.CharField(max_length=255, null=True, blank=True, verbose_name="Office ID") # choices=OFFICE_ID_CHOICES, 
    ## should officename have choices if we don't FK to OfficeName model?
    # office_name = models.ForeignKey(OfficeName, null=True)
    officename = models.CharField(max_length=255, null=True, blank=True, verbose_name="Office name")
    party = models.CharField(max_length=255, null=True, blank=True, help_text="Always enter unless it's a ballot measure.") # choices=PARTY_CHOICES, 
    polid = models.CharField(max_length=255, null=True, verbose_name="Politician ID")
    polnum = models.CharField(max_length=255, null=True, verbose_name="Politician Number")
    precinctsreporting = models.IntegerField(null=True, verbose_name="Precincts reporting")
    precinctsreportingpct = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True, verbose_name="Precincts reporting %") # validators=[MinValueValidator(0), MaxValueValidator(100)], 
    precinctstotal = models.IntegerField(null=True, verbose_name="Precincts total")
    ## foreign key race_id_date to race.race_id_date model or one of the many from a one-to-many in election.electiondate? and/or separate fk for electiondate
    # race_id_date = models.CharField(max_length=255, null=True)
    # race_id: # AP-assigned race ID. Since race IDs are guaranteed to be unique only within a state, you must use this parameter in conjunction with the statePostal parameter. Multiple values must be for the same state and must be separated by commas.
    raceid = models.CharField(max_length=255, null=True, verbose_name="Race ID", help_text="Assigned by AP.")
    racetype = models.CharField(max_length=255, null=True, verbose_name="Race type")
    racetypeid = models.CharField(max_length=1, null=True, verbose_name="Race type ID", help_text="Assigned by AP.")
    reportingunitid = models.CharField(max_length=255, null=True, verbose_name="Reporting Unit ID", help_text="Assigned by AP.")
    reportingunitname = models.CharField(max_length=255, null=True, verbose_name="Reporting unit name", help_text="Name of county, township, etc.")
    runoff = models.BooleanField(default=False, help_text="Is this result for a runoff election? Only select if so. Don't check the box if this is for a race that could lead to a runoff. Instead, include that in the \"note\" field of the related race.")
    seatname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat name")
    seatnum = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat number", help_text="Assigned by AP.")
    statename = models.CharField(max_length=255, null=True, verbose_name="State name")
    statepostal = models.CharField(max_length=2, null=True, verbose_name="State postal") # choices=STATE_POSTAL_CHOICES, 
    ## test field is in common field, so leave commented out or delete
    # test = models.BooleanField(default=False)
    uncontested = models.NullBooleanField(default=False)
    # votecount = models.IntegerField(null=True, verbose_name="Vote count")
    votecount = models.DecimalField(max_digits=9, decimal_places=0, null=True, verbose_name="Vote count", help_text="Enter 0 if the results are not yet available.")
    votepct = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True, verbose_name="Vote %")
    ## if votingsystem is activated, be sure to activate in election_loaders for ResultCsv to ResultManual function
        # also, be sure to update ResultManual save method so the value in Race populates the comparable value
    # votingsystem = models.CharField(choices=VOTING_SYSTEM_CHOICES, max_length=255, null=True, blank=True, verbose_name="Voting system", help_text="Required for manual entry of local races.")
    winner = models.NullBooleanField(default=False) # , help_text="Elex converts to true/false from four AP choices."
    
    def votepct_formatted(self):
        if self.votepct and self.datasource != "Associated Press":
            reformatted_votepct = str(int(round(self.votepct))) + '%'
        elif self.votepct and self.datasource == "Associated Press":
            reformatted_votepct = str(int(round(self.votepct*100))) + '%'
        else:
            reformatted_votepct = None
        return reformatted_votepct
    votepct_formatted.admin_order_field = 'votepct'
    votepct_formatted.short_description = 'Vote %'

    def precinctsreportingpct_formatted(self):
        if self.precinctsreportingpct and self.datasource != "Associated Press":
            reformatted_precinctsreportingpct = str(int(round(self.precinctsreportingpct))) + '%'
        elif self.precinctsreportingpct and self.datasource == "Associated Press":
            reformatted_precinctsreportingpct = str(int(round(self.precinctsreportingpct*100))) + '%'
        else:
            reformatted_precinctsreportingpct = None
        return reformatted_precinctsreportingpct
    precinctsreportingpct_formatted.admin_order_field = 'precinctsreportingpct'
    precinctsreportingpct_formatted.short_description = format_html('Precincts <br>reporting %')

    class Meta:
        verbose_name = 'Results - MASTER'
        verbose_name_plural = 'Results - MASTER'
        # ordering = ['-lastupdated']
        ordering = ['-created']
        # ordering = ['-updated_system'] # inherited from CommonInfo
        # abstract = True

    def __unicode__(self):
        return "%s %s" % (self.first, self.last)
        # return "%s votes cast with %s precincts reporting" % (self.vote_count, self.precincts_reportingpct)

    # def election_date_string(self):        
    #     return '%s' % self.electiondate ## !!! Models must be connected to other scripts before this can be uncommented or else it will conflict with var definition already in scripts


class ResultLive(Result):
 
    class Meta:
        verbose_name = 'Results - live'
        verbose_name_plural = 'Results - live'
        # ordering = ['-lastupdated']
        # ordering = ['-updated_ap']
        # ordering = ['-updated_system'] # inherited from CommonInfo
        ## PROXY inheritance https://docs.djangoproject.com/en/1.9/topics/db/models/#proxy-models 
        # proxy = True


class ResultPosted(ResultLive):
    ## !!!! WHAT SHOULD ResultPosted INHERIT? !!!
        ## if it inherits ResultLive, then the following is needed need:
            ## I need to update the resource for ResultLive to actually pull from ResultLive and not ResultStage
            ## I need to set up a resource for ResultStage -- and/or just rename it ResultAP or something
            ## Danny to switch his ResultManual to pull from ResultLive 
            ## Danny to switch his ResultLive to pull from ResultStage
        ## or just point ResultManual resource to ResultLive model, which I've done commented out in resources.py

    # def save(self, *args, **kwargs):
        # if not self.id:
            ## generate id: based on electiondate + something else?
            # self.id = 
        # return super(ResultPosted, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Results - posted via API'
        verbose_name_plural = 'Results - posted via API'


class ResultManual(ResultLive):
    ## functions to limit what is visible in the admin
    def limit_race_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"dataentry": "manual", "electiondate__gte": time_offset}

    def limit_candidate_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"dataentry": "manual", "electiondate__gte": time_offset}

    def limit_election_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"electiondate__gte": time_offset}

    def limit_reportingunit_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"electiondate__gte": time_offset}

    candidate_name_fk = models.ForeignKey(Candidate, null=True, verbose_name="Candidate name or Ballot Measure option", help_text="If this is for a ballot measure, choose or add: Yes, No or whatever the responses are on the ballot.", limit_choices_to=limit_candidate_choices)
    ## election_fk not needed bc election date now pulling from race_name_fk, but needed for enabling the inline
    election_fk = models.ForeignKey(Election, null=True, verbose_name="Election", limit_choices_to=limit_election_choices)
    gdoc_import = models.BooleanField(default=False, verbose_name="gdoc import?")
    race_name_fk = models.ForeignKey(Race, null=True, verbose_name="Race: State / Party / Type / Date / Office / Seat", help_text="Only add or choose a race with a party if it's a primary or caucus. Make sure it's the correct one by selected and clicking the pen to edit/view details.", limit_choices_to=limit_race_choices)
    reporting_unit_fk = models.ForeignKey(ReportingUnit, null=True, verbose_name="Reporting unit", help_text="Name of county, township, etc.", limit_choices_to=limit_reportingunit_choices)
    votepct_caculated = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True, verbose_name="Vote %", help_text="Automatically calculated by the system.")
    
    ## add validators??? validators=[MinValueValidator(0), MaxValueValidator(100)]
        ## https://docs.djangoproject.com/en/1.9/ref/validators/

    ## use foreign key fields to populate all the model fields that are not filled out by a user
            ## national, runoff, votecount, winner, test are in admin and don't need to be updated
    def save(self, *args, **kwargs):
        if not self.gdoc_import:          
            now = timezone.localtime(timezone.now())
            self.lastupdated = now
            ## do we need this? might be helpful
            try:
                self.datasource = self.race_name_fk.datasource_fk.source_name
            except:
                pass        
            if not self.dataentry: 
                self.dataentry = "manual"
            try:
                self.description = self.race_name_fk.description
            except:
                pass
            self.electiondate = self.election_fk.electiondate
            try:
                self.first = self.candidate_name_fk.first
            except:
                pass
            self.raceid = self.race_name_fk.raceid
            self.racetype = self.race_name_fk.racetype
            if self.racetype == "Ballot Issue":
                self.is_ballot_measure = True
            else:
                self.is_ballot_measure = False
            # try:
            #     if self.race_name_fk.is_ballot_measure:
            #         self.is_ballot_measure = self.race_name_fk.is_ballot_measure
            #     elif self.race_name_fk.racetype == "Ballot Issue":
            #         self.racetype = self.race_name_fk.racetype
            #         self.is_ballot_measure = True
            #     else:
            #         pass
            # except:
            #     pass
            self.last = self.candidate_name_fk.last
            try:
                if self.systemupdated:
                    self.lastupdated = self.systemupdated
            except:
                pass
            self.level = self.reporting_unit_fk.level
            try:
                self.note = self.race_name_fk.note
            except:
                pass
            try:
                self.officename = self.race_name_fk.officename_fk.officename
            except:
                pass
            self.party = self.candidate_name_fk.party
            try:
                self.precinctsreporting = self.reporting_unit_fk.precinctsreporting
            except:
                pass
            try:
                self.precinctsreportingpct = self.reporting_unit_fk.precinctsreportingpct
            except:
                pass
            try:
                self.precinctstotal = self.reporting_unit_fk.precinctstotal
            except:
                pass
            self.reportingunitname = self.reporting_unit_fk.location_fk.locationname
            try:
                self.seatname = self.race_name_fk.seatname_fk.seatname
            except:
                pass 
            self.statepostal = self.reporting_unit_fk.statepostal

        return super(ResultManual, self).save(*args, **kwargs)

    def votepct_formatted(self):
        if self.votepct:
            reformatted_votepct = str(int(round(self.votepct))) + '%'
        else:
            reformatted_votepct = None
        return reformatted_votepct
    votepct_formatted.admin_order_field = 'votepct'
    votepct_formatted.short_description = 'Vote %'

    def precinctsreportingpct_formatted(self):
        if self.precinctsreportingpct:
            reformatted_precinctsreportingpct = str(int(round(self.precinctsreportingpct))) + '%'
        else:
            reformatted_precinctsreportingpct = None
        return reformatted_precinctsreportingpct
    precinctsreportingpct_formatted.admin_order_field = 'precinctsreportingpct'
    precinctsreportingpct_formatted.short_description = format_html('Precincts <br>reporting %')

    def candidate_name_fk_reformatted(self):
        return self.candidate_name_fk
    candidate_name_fk_reformatted.admin_order_field = 'last'
    candidate_name_fk_reformatted.short_description = 'Name/option'

    def reportingunitname_reformatted(self):
        return self.reportingunitname
    reportingunitname_reformatted.admin_order_field = 'reportingunitname'
    reportingunitname_reformatted.short_description = 'Reporting unit'

    def __unicode__(self):
        if self.gdoc_import:
            if self.first:
                candidate_name = '%s %s' % (self.first, self.last)
            else:
                candidate_name = self.last
            return "Candidate: %s, Race: %s , RU: %s" % (candidate_name, self.officename, self.reportingunitname)
        else:
            return "Candidate: %s , Race: %s , RU: %s" % (self.candidate_name_fk, self.race_name_fk, self.reporting_unit_fk)

    class Meta:
        verbose_name = 'STEP 8: Results - manual'
        verbose_name_plural = 'STEP 8: Results - manual'
        ordering = ['officename']

## calculate votes
@receiver(post_save, sender=ResultManual, dispatch_uid="call_calculate_vote_command")
def calculate_vote(sender, instance, **kwargs):
    ## don't fire if it's a gdoc result
    if instance.gdoc_import != True:
        electiondate_arg = str(instance.electiondate)
        call_command('calculate_vote', electiondate_arg)
        ## needs to be written <-- not doing this bc it would mess with manual results w/ multiple winners, winners that req 2/3, etc
        # call_command('declare_winner')


## NEEDS TO STAY models.model so PSQL import works
class ResultStage(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=1)
    ## removed from Elex --> # uniqueid = models.CharField(max_length=255, null=True, blank=True) 
    raceid = models.CharField(max_length=255, null=True, help_text="AP-assigned race ID.")
    racetype = models.CharField(max_length=255, null=True, help_text="e.g. General, Special General, Primary, Caucus, Ballot Issue.")
    racetypeid = models.CharField(max_length=1, null=True)    
    ballotorder = models.IntegerField(null=True, help_text="Ballot order of this candidate or issue. For AP data, there may be gaps in sequence.")
    candidateid = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    delegatecount = models.PositiveIntegerField(null=True, blank=True)
    electiondate = models.DateField(null=True, verbose_name="Election date")
    electtotal = models.PositiveIntegerField(null=True, blank=True)
    electwon = models.PositiveIntegerField(null=True, blank=True)
    fipscode = models.CharField(max_length=255, null=True)
    first = models.CharField(max_length=255, null=True, blank=True)
    incumbent = models.BooleanField(default=False)
    initialization_data = models.BooleanField(default=False)
    is_ballot_measure = models.BooleanField(default=False, verbose_name="Ballot measure")
    last = models.CharField(max_length=255, null=True, blank=True)
    lastupdated = models.DateTimeField(max_length=255, null=True, verbose_name="Updated by AP", help_text="This is when the item was last updated by AP.")    
    level = models.CharField(max_length=255, null=True)
    national = models.BooleanField(default=False)
    officeid = models.CharField(max_length=255, null=True, blank=True) 
    officename = models.CharField(max_length=255, null=True, blank=True, verbose_name="Office name")
    party = models.CharField(max_length=255, null=True, blank=True)
    polid = models.CharField(max_length=255, null=True)
    polnum = models.CharField(max_length=255, null=True)
    precinctsreporting = models.IntegerField(null=True)
    precinctsreportingpct = models.DecimalField(max_digits=20, decimal_places=3,  null=True, blank=True, verbose_name="% precincts reporting")
    precinctstotal = models.IntegerField(null=True)
    reportingunitid = models.CharField(max_length=255, null=True)
    reportingunitname = models.CharField(max_length=255, null=True, verbose_name="Reporting unit name", help_text="County, township, etc.")
    runoff = models.BooleanField(default=False)
    seatname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat name")
    seatnum = models.CharField(max_length=255, null=True, blank=True)
    statename = models.CharField(max_length=255, null=True)
    statepostal = models.CharField(max_length=2, null=True, verbose_name="State")
    test = models.BooleanField(default=False)
    uncontested = models.BooleanField(default=False)
    votecount = models.IntegerField(null=True, verbose_name="Vote count")
    votepct = models.DecimalField(max_digits=20, decimal_places=3, null=True, verbose_name="Vote %")
    winner = models.BooleanField(default=False)
    
    def precinctsreportingpct_formatted(self):
        if self.precinctsreportingpct:
            reformatted_precinctsreportingpct = str(int(round(self.precinctsreportingpct*100))) + '%'
        else:
            reformatted_precinctsreportingpct = None 
        return reformatted_precinctsreportingpct
    precinctsreportingpct_formatted.admin_order_field = 'precinctsreportingpct'
    precinctsreportingpct_formatted.short_description = format_html('Precincts <br>reporting %')

    ## reformat votecount to include commas as needed
    def votecount_formatted(self):
        return "{:,}".format(self.votecount)
    votecount_formatted.short_description = 'Vote count'

    def votepct_formatted(self):
        if self.votepct:
            reformatted_votepct = str(int(round(self.votepct*100))) + '%'
        else:
            reformatted_votepct = None
        return reformatted_votepct
    votepct_formatted.admin_order_field = 'votepct'
    votepct_formatted.short_description = 'Vote %'

    class Meta:
        verbose_name = 'Results - staged'
        verbose_name_plural = 'Results - staged'
        ordering = ['-lastupdated']


## a mirror of ResultStage          
class ResultCheck(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=1)
    raceid = models.CharField(max_length=255, null=True, help_text="AP-assigned race ID.")
    racetype = models.CharField(max_length=255, null=True, help_text="e.g. General, Special General, Primary, Caucus, Ballot Issue.")
    racetypeid = models.CharField(max_length=1, null=True)    
    ballotorder = models.IntegerField(null=True, help_text="Ballot order of this candidate or issue. For AP data, there may be gaps in sequence.")
    candidateid = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    delegatecount = models.PositiveIntegerField(null=True, blank=True)
    electiondate = models.DateField(null=True, verbose_name="Election date")
    electtotal = models.PositiveIntegerField(null=True, blank=True)
    electwon = models.PositiveIntegerField(null=True, blank=True)
    fipscode = models.CharField(max_length=255, null=True)
    first = models.CharField(max_length=255, null=True, blank=True)
    incumbent = models.BooleanField(default=False)
    initialization_data = models.BooleanField(default=False)
    is_ballot_measure = models.BooleanField(default=False, verbose_name="Ballot measure")
    last = models.CharField(max_length=255, null=True, blank=True)
    lastupdated = models.DateTimeField(max_length=255, null=True, verbose_name="Last updated", help_text="This is when the item was last updated.")    
    level = models.CharField(max_length=255, null=True)
    national = models.BooleanField(default=False)
    officeid = models.CharField(max_length=255, null=True, blank=True)
    officename = models.CharField(max_length=255, null=True, blank=True, verbose_name="Office name")
    party = models.CharField(max_length=255, null=True, blank=True)
    polid = models.CharField(max_length=255, null=True)
    polnum = models.CharField(max_length=255, null=True)
    precinctsreporting = models.IntegerField(null=True)
    precinctsreportingpct = models.DecimalField(max_digits=20, decimal_places=3,  null=True, blank=True, verbose_name="% precincts reporting")
    precinctstotal = models.IntegerField(null=True)
    reportingunitid = models.CharField(max_length=255, null=True)
    reportingunitname = models.CharField(max_length=255, null=True, verbose_name="Reporting unit name", help_text="County, township, etc.")
    runoff = models.BooleanField(default=False)
    seatname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat name")
    seatnum = models.CharField(max_length=255, null=True, blank=True)
    statename = models.CharField(max_length=255, null=True)
    statepostal = models.CharField(max_length=2, null=True, verbose_name="State")
    test = models.BooleanField(default=False)
    uncontested = models.BooleanField(default=False)
    votecount = models.IntegerField(null=True, verbose_name="Vote count")
    votepct = models.DecimalField(max_digits=20, decimal_places=3, null=True, verbose_name="Vote %")
    winner = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Results - check'
        verbose_name_plural = 'Results - check'
        ordering = ['-lastupdated']


class ResultCsv(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID", help_text="Constructed using election date and spreadsheet row")
    last = models.CharField(max_length=255, null=True, blank=True, verbose_name="Candidate last name")
    first = models.CharField(max_length=255, null=True, blank=True, verbose_name="Candidate first name")
    reportingunitname = models.CharField(max_length=255, null=True, verbose_name="Reporting unit name")
    level = models.CharField(max_length=255, null=True, verbose_name="Reporting unit level")
    raceid = models.CharField(max_length=255, null=True)
    racetype = models.CharField(max_length=255, null=True, verbose_name="Race type")
    officename = models.CharField(max_length=255, null=True, blank=True, verbose_name="Office name")
    seatname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat name")
    seatnum = models.CharField(max_length=255, null=True, blank=True, verbose_name="Seat number")
    precinctsreporting = models.IntegerField(null=True, verbose_name="Precincts reporting")
    precinctsreportingpct = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True, verbose_name="Precincts reporting %") 
    precinctstotal = models.IntegerField(null=True, verbose_name="Precincts total")
    votecount = models.DecimalField(max_digits=9, decimal_places=0, null=True, verbose_name="Vote count")
    votepct = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True, verbose_name="Vote percent")
    winner = models.NullBooleanField(default=False)
    # live = models.BooleanField(default=False)
    ballotorder = models.IntegerField(null=True, blank=True, verbose_name="Ballot order")
    note = models.CharField(max_length=255, null=True, blank=True)
    electiondate = models.DateField(null=True, verbose_name="Election date")
    fipscode = models.CharField(max_length=255, null=True)
    incumbent = models.NullBooleanField(default=False)
    is_ballot_measure = models.NullBooleanField(default=False, verbose_name="Ballot measure")
    nonpartisan = models.CharField(max_length=255, null=True, blank=True, verbose_name="Non-partisan?")
    party = models.CharField(max_length=255, null=True, blank=True, help_text="Spreadsheet options: Dem, GOP, Ind, Other.")
    statepostal = models.CharField(max_length=2, null=True, verbose_name="State")
    # test = models.BooleanField(default=False)
    uncontested = models.NullBooleanField(default=False)
    votingsystem = models.CharField(choices=VOTING_SYSTEM_CHOICES, max_length=255, null=True, blank=True, verbose_name="Voting system")
    lastupdated = models.DateTimeField(null=True, blank=True, verbose_name="Last updated")
     
    class Meta:
        verbose_name = 'Results - csv import'
        verbose_name_plural = 'Results - csv import'
        ordering = ['-lastupdated']

    def __unicode__(self):
        return "%s %s" % (self.first, self.last)
        # return "%s votes cast with %s precincts reporting" % (self.vote_count, self.precincts_reportingpct)


class Embed(BasicInfo):
    ## functions to limit what is visible in the admin
    def limit_election_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"electiondate__gte": time_offset}

    def limit_race_choices():
        today = timezone.localtime(timezone.now()).date()
        time_offset = today - timedelta(days=60)
        return {"electiondate__gte": time_offset}
        # return {"electiondate__gte": time_offset, "dataentry": manual}

    election_fk = models.ForeignKey(Election, null=True, verbose_name="Election", help_text="An election is a superset of races and ballot measures.", limit_choices_to=limit_election_choices)
    embed_code = models.TextField(null=True, blank=True, help_text="Copy the entire code snippet above (including the < > angle brackets).")
    embed_type = models.CharField(max_length=255, choices=EMBED_CHOICES)
    label = models.CharField(max_length=30, null=True, blank=True, help_text="Optional.Short description of the races included (e.g. Local Results, Election 2016, Decision 2016, etc). Only displays if there's a \"view more results link\" entered. Limit: 30 characters.")
    name = models.CharField(max_length=255, null=False, blank=False)
    race_mm = models.ManyToManyField(Race, blank=True, related_name="races", verbose_name="Races", help_text="NOTE: There's a three-race limit for horizontal embeds.", limit_choices_to=limit_race_choices)
    view_more_results_link = models.URLField(max_length=255, null=True, blank=True, help_text="Optional. If you have a landing page or article housing all of your results, you can tease that in the horizontal embed.")


    def save(self, *args, **kwargs):
        embed_set = ''
        if self.created:
            if self.race_mm.count() == 0:
                embed_set += "<!-- !!! WARNING !!! You haven't selected any races, so your embed set is currently empty. Please select 2 or 3 races for a horizontal embed or any number more than 1 for a vertical embed. -->"
            else:
                ## if applicable, add label for the embed set
                if self.label and self.view_more_results_link:
                    label_code = '<!-- LABEL --><div class="heading"><a href="%s">%s</a></div>' % (self.view_more_results_link, self.label)
                    embed_set += label_code
                ## check which type of embed set
                if self.embed_type == 'horizontal':
                    horizontal_embed = '<!-- HORIZONTAL EMBED -->'
                    embed_set += horizontal_embed
                    if self.race_mm.count() >3:
                        embed_set = "<!-- !!! WARNING !!! You have entered more than 3 races for a horizontal embed. This is not supported. Please choose only three and re-save or switch this to a vertical embed. -->"
                    else:
                        try:
                            if self.race_mm.count() == 2: 
                                ## open the div
                                horizontal_embed_two = '<!-- WRAPPER for 2 RACES --><div id="election-embeds-full">'
                                embed_set += horizontal_embed_two
                                ## loop thru all the races associated with an individual embed object
                                counter = 0
                                for race in self.race_mm.iterator():
                                    counter += 1
                                    ## add the race wrapper
                                    if counter != 2:
                                        embed_set += '<div class="col-sm-6 border-right border-xs-remove-right">'
                                    else:
                                        embed_set += '<div class="col-sm-6">'
                                    ## add embed code 
                                    embed_set += str(race.embed_code)
                                    ## close the race wrapper div
                                    embed_set += '</div>'
                                ## close the embeds set wrapper div
                                embed_set += '</div>'
                            elif self.race_mm.count() == 3: 
                                ## open the div
                                horizontal_embed_three = '<!-- WRAPPER for 3 RACES --><div id="election-embeds-full">'
                                embed_set += horizontal_embed_three
                                ## loop thru all the races associated with an individual embed object
                                counter = 0
                                for race in self.race_mm.iterator():
                                    counter += 1
                                    ## add the race wrapper
                                    if counter != 3:
                                        embed_set += '<div class="col-sm-4 col-xs-12 border-right border-xs-remove-right">'
                                    else: 
                                        embed_set += '<div class="col-sm-4 col-xs-12">'
                                    ## add embed code 
                                    embed_set += str(race.embed_code)
                                    ## close the race wrapper div
                                    embed_set += '</div>'
                                ## close the embed set wrapper
                                embed_set += '</div>'
                        except:
                            pass
                elif self.embed_type == 'vertical':
                    try:
                        ## open the div
                        vertical_embed = '<!-- VERTICAL EMBED: PARTIAL-WIDTH --><div id="election-embeds-inline">'
                        embed_set += vertical_embed
                        ## loop thru all the races associated with an individual embed object
                        for race in self.race_mm.iterator():
                            ## add that code 
                            embed_set += str(race.embed_code)
                        ## close the div
                        embed_set += '</div>'
                    except:
                        pass
                elif self.embed_type == 'unformatted':
                    ## open the div
                    vertical_embed = '<!-- VERTICAL EMBED: FULL-WIDTH -->'
                    embed_set += vertical_embed
                    ## loop thru all the races associated with an individual embed object
                    for race in self.race_mm.iterator():
                        ## add that code 
                        embed_set += str(race.embed_code)
                ## if applicable, add the view more link 
                if self.view_more_results_link:
                    view_more_code = '<div class="clearfix"></div><!-- READ MORE LINK --><div class="view-more-latest readmore"><a href="%s">View more results</a></div>' % (self.view_more_results_link)
                    embed_set += view_more_code
            self.embed_code = embed_set  
        return super(Embed, self).save(*args, **kwargs)

    # def __unicode__(self):
    #     return "%s for %s (%s)" % (self.name, self.election_fk.electiondate, self.embed_type)

    class Meta:
        verbose_name = "STEP 9: Embed set"
        ordering = ['-systemupdated']



## validation for number of race_mm selected
    ## but not ideal bc it just raises a validation error, not an admin error
# from django.db.models.signals import m2m_changed
# from django.core.exceptions import ValidationError
# from django.contrib import messages
# from django import forms

# def regions_changed(sender, **kwargs):
#     if kwargs['instance'].race_mm.count() > 3:
#         # messages.error(request, "No more than 3 races are allowed in the horizontal embed")
#         raise forms.ValidationError('No more than 3 races are allowed in the horizontal embed')

# m2m_changed.connect(regions_changed, sender=Embed.race_mm.through)

