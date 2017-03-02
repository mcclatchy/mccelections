'''
This doesn't currently work. To debug:

- Check csv permissions
- Check that db user is a super user
- Check postgres config

'''

from django.core.management.base import BaseCommand, CommandError
# from elexconnection import election_date_string
from results.models import ResultStage
from postgres_copy import CopyMapping
import time
import datetime
import os


election_date_string="2016-02-09"
save_date_string="2016-02-11"
sleep_time=30

## local example
# file_directory = "/<YOUR>/<PATH>/mccelections/electionsproject/snapshots/%s/%s" % (election_date_string, save_date_string)
## prod server
file_directory = "/home/ubuntu/mccelections/electionsproject/snapshots/%s/%s" % (election_date_string, save_date_string)

def delete_all_resultstage_objects(self):
    ResultStage.objects.all().delete()
    self.stdout.write('Deleting all objects in ResultStage table')

class Command(BaseCommand):
    help = 'Import results to Result Stage model for %s' % (election_date_string)

    def handle(self, *args, **options):
        d = datetime.datetime
        
        start_time = d.now()
        self.stdout.write('\n')        

        initial_message = 'About to loop through all files saved in %s directory and update Result Stage table for %s. \n' % (save_date_string, election_date_string)

        self.stdout.write(initial_message)

        for file in os.listdir(file_directory):
            
            full_file_path = file_directory + '/' + file
            delete_all_resultstage_objects(self)

            start_message = 'Started loading file at ' + str(unicode(start_time)) + ' for ' + election_date_string

            c = CopyMapping(
                # Give it the model
                ResultStage,
                # The path to your CSV
                full_file_path,
                # And a dict mapping the model fields to CSV headers
                dict(id='id', unique_id='unique_id', raceid='raceid', racetype='racetype',  racetypeid='racetypeid', ballotorder='ballotorder',  candidateid='candidateid', description='description', electiondate='electiondate', fipscode='fipscode', first='first', incumbent='incumbent', initialization_data='initialization_data',  is_ballot_measure='is_ballot_measure', last='last', lastupdated='lastupdated',  level='level', national='national',  officeid='officeid', officename='officename',  party='party', polid='polid', polnum='polnum', precinctsreporting='precinctsreporting', precinctsreportingpct='precinctsreportingpct', precinctstotal='precinctstotal',reportingunitid='reportingunitid', reportingunitname='reportingunitname', runoff='runoff', seatname='seatname', seatnum='seatnum', statename='statename', statepostal='statepostal', test='test', uncontested='uncontested', votecount='votecount',  votepct='votepct', winner='winner')
            )
            
            loading_message = 'Loading %s.' % (full_file_path)
            self.stdout.write(loading_message)
            # initial_message = '%s.' % ()
            self.stdout.write('\n')

            c.save()
            self.stdout.write('Saved')

            end_time = d.now()
            import_length = str(unicode(end_time - start_time))
            end_message = 'Finished copying snapshot at ' + str(unicode(end_time))
            self.stdout.write('\n')

            self.stdout.write(end_message)
            self.stdout.write('\n')

            self.stdout.write('Loading this snapshot took ' + import_length)

            self.stdout.write('Sleeping for %s') % (sleep_time)
            time.sleep(sleep_time)
            self.stdout.write('--------------------------------------')


    
        
