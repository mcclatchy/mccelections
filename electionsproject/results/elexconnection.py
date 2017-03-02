from elex.api.models import Election as ElexElection


## Setup and call the AP elections API via elex
def election_connection(electiondate_arg, live_arg, test_arg):
    connection = ElexElection(electiondate=electiondate_arg, testresults=test_arg, liveresults=live_arg, is_test=test_arg)

    return connection