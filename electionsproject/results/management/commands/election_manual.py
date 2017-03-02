from django.core.management.base import BaseCommand, CommandError

'''

for manual test elections (e.g. AP tests)
- be sure to account for NOT importing test data on prod
- see if we can use env var

'''

def manual_election():

    ## set election object
    election = 

    live_election = election.live

    while live_election:
        ## import

class Command(BaseCommand):
    help = 'Live election functions.'

    def handle(self, *args, **options):
        ## call function(s)

        if mccelectionsenv != "prod":
            # load the function