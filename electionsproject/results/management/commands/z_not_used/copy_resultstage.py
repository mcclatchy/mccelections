from django.core.management.base import BaseCommand, CommandError
from results.models import ResultStage, ResultLive

## rename prefix to copy_ 
def add_resultstage_to_resultlive():
	## main vars/querysets
	resultstage_objects = ResultStage.objects.all()
	resultlive_objects = ResultLive.objects.all()
	result_objects_filtered = ResultLive.objects.filter(source="Associated Press")
	
	## remove old resultstage objects from resultlive before adding new ones
	# result_objects_filtered.delete()
	
	## loop thru and add new ones
	for obj in result_stage_objects:

	
		
class Command(BaseCommand):
    help = 'Calculate total votes per race and update each ResultManual object'

    def handle(self, *args, **options):
    	add_resultstage_to_resultlive()
    	self.stdout.write('Updated ResultLive with ResultStage data')
