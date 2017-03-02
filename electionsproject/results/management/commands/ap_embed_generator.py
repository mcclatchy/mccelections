from results.models import Race
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Generate state-by-state files of individual AP embed codes'

    def handle(self, *args, **options):

        mcclatchy_states = ["CA","FL","GA","ID","IL","KS","KY","MO","MS","NC","PA","SC", "TX", "WA"]

        for state in mcclatchy_states:

            filename = "/Users/glinch/code/mccelections-misc/embed_ap/%s.html" % (state)

            with open(filename, "w") as file:

                election_date_arg = "2016-11-08"

                races = Race.objects.filter(dataentry="automated", electiondate=election_date_arg, statepostal=state)

                # counter = 0

                contents = ""

                for race in races:
                    # state_label = "<!-- STATE: %s -->" % (state)
                    # contents += state_label
                    # counter += 1
                    race_label = "<!-- " + str(race) + " -->"
                    preprended_code = '<link rel="stylesheet" type="text/css" href="http://media.mcclatchydc.com/static/elections/2016/general/css/APindividualrace.css"></link><div class="ap-state-race-table">'
                    embed_code = str(race.embed_code_ap)
                    appended_code = "</div>"
                    contents += race_label + preprended_code + embed_code + appended_code + "\n\n"

                file.write(contents)

                file.close()

            # print counter

            '''
            loop thru all races
                loop thru all states
                    create a new file with those

            '''