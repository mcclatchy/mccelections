from django.core.management.base import BaseCommand, CommandError
from results.models import Embed
from results.slackbot import slackbot


class Command(BaseCommand):
    help = 'Save embed set based on the ID.'


    def add_arguments(self, parser):
        ## required, positional arguments
        parser.add_argument('id', nargs='+', type=str)

    #     parser.add_argument('-i', '--id',
    #         # action='store_true',
    #         type=str,
    #         dest='id',
    #         # default=False,
    #         help='This is the ID from the related Embed object.'
    #     )

    def handle(self, *args, **options):

        id_arg = int(options['id'][0])

        message = "Embed ID:\t\t" + str(id_arg)
        slackbot(message)

        ## use queryset to filter object, check there's only 1 and save
        embeds = Embed.objects.all()
        embeds_filtered = embeds.filter(id=id_arg)
        if embeds_filtered.count() == 1:
            embed_object = embeds_filtered[0]
            embed_object.save()

            message = "Saved:\t\t%s\n\n" % (str(embed_object))
            slackbot(message)
        else: 
            message = "More than one object was found. Please fix and re-try."
            slackbot(message)
