from django.core.management.base import BaseCommand, CommandError
# from electionsproject.settings import mccelectionsenv
from django.core.management import call_command
from results.slackbot import slackbot
import time


class Command(BaseCommand):
    help = 'Automatically run the two main election scripts: download_elections and election_auto.'

    def handle(self, *args, **options):
		run = True
		while run:
			## import new AP elections, if any
			call_command('download_elections')

			## check if there's an Election today; if so, start checking every minute whether to set live and start import
			call_command('election_auto')

			## Sleep this script
			# if mccelectionsenv == "local":
				# hours = 6 ## because if the next day is a test, we'll want to be able to capture that
				## but how do we handle locally if a previous live election is still going and there's a test? need to stop and restart election_auto on correct day
			hours = 1
			election_sleep = 60 * 60 * hours ## seconds * minutes * hours
			plural = "s" if hours > 1 else ""
			message = "Sleeping download_elections and election_auto for %d hour%s" % (hours, plural)
			slackbot(message)
			# print message
			time.sleep(election_sleep)