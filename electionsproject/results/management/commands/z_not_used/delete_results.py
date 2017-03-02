from django.core.management.base import BaseCommand, CommandError
from results.models import Result
from results.elexconnection import election_date_string


def delete_model_objects(self):
    Result.objects.filter(election_date=election_date_string).delete()


class Command(BaseCommand):
    help = 'Delete all items in result model for %s' % (election_date_string)

    def handle(self, *args, **options):
        delete_model_objects(self)
        self.stdout.write('')
        self.stdout.write('Result model objects deleted.')
        self.stdout.write('')