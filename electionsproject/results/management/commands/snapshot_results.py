from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from results.models import Result
from results.elexconnection import election_date_string
import datetime


def snapshot_to_json(self):
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    ## don't include trailing slash in path -- it's in fullpath
    
    ## server (change parent dir to fixtures, add that path to Django settings and just leave dated subdirectory)
    path = '/home/ubuntu/mccelections/electionsproject/snapshots/%s' % (election_date_string)

    filename = '%s' % (now)
    fullpath = '%s/%s.json' % (path, filename)

    snapshotresults = serializers.serialize('json', Result.objects.filter(election_date=election_date_string))

    f = open(fullpath, 'w')
    f.write(snapshotresults)
    f.close()


class Command(BaseCommand):
    help = 'Snapshot results for %s election' % (election_date_string)

    def handle(self, *args, **options):
        ## can this be abstracted like is possible for the import_ap_elex* commands?
        d = datetime.datetime
        message = 'Results for %s election have been saved.' % (election_date_string)
        
        start_time = d.now()
        self.stdout.write('\n')        
        start_message = 'Started snapshot at ' + str(unicode(start_time))
        
        self.stdout.write(start_message)
        self.stdout.write('\n')

        ## execute function
        snapshot_to_json(self)
        
        self.stdout.write(message)
        
        end_time = d.now()
        import_length = str(unicode(end_time - start_time))
        end_message = 'Finished snapshot at ' + str(unicode(end_time))
        self.stdout.write('\n')

        self.stdout.write(end_message)
        self.stdout.write('\n')

        self.stdout.write('Snapshotting took ' + import_length)
        self.stdout.write('--------------------------------------')
