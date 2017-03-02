from django.core.management.base import BaseCommand, CommandError
from results.models import ResultStage, ResultCheck


def count_result(model_arg):
    if model_arg == "resultcheck":
        result_count = ResultCheck.objects.all().count()
    else:
        result_count = ResultStage.objects.all().count()
    return result_count

def delete_result(model_arg):
    if model_arg == "resultcheck":
        ResultCheck.objects.all().delete()
    else:
        ResultStage.objects.all().delete()

def count_delete_result(model_arg):
    count = str(count_result(model_arg))
    delete_result(model_arg)
    message = '%s objects deleted:\t%s' % (model_arg, count)
    
    print "\n" + message + "\n"

class Command(BaseCommand):
    help = 'Delete all items in ResultStage or ResultCheck model.'

    def add_arguments(self, parser):
        ## positional requred arguments
        parser.add_argument('model', 
            # action='store_true',
            # dest='model',
            # default='result',
            help='Specify the model (resultstage or resultcheck) you want to delete'
        )

    def handle(self, *args, **options):
        model_arg = options['model']

        count_delete_result(model_arg)