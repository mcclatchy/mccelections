from slacker import Slacker
from electionsproject.settings import mccelectionsenv
from electionsproject.settings_private import SLACK_TOKEN
import os


def slackbot(text):
    """
    Posts messages to Slack channel based on environment
    """

    slack = Slacker(SLACK_TOKEN)
    username = "electionsbot"
    icon_url = "https://c1.staticflickr.com/6/5667/20571587160_92070a9546_b.jpg"
    # icon_url = "https://pixabay.com/static/uploads/photo/2013/07/13/13/41/robot-161368_960_720.png"

    ## set channel based on the environment: local, test, prod
    if mccelectionsenv == "local":
        channel = "#electionserverlocal"
    elif mccelectionsenv == "test":
        channel = "#electionservertest"
    elif mccelectionsenv == "prod":
        channel = "#electionserverprod"
    
    ## uses try statement in order to avoid requests package error:
        # Max retries exceeded with url
    try:
        slack.chat.post_message(channel, text, username=username, link_names=True, icon_url=icon_url)

        # return "Messaged posted: %s" % (text)
    
    except:
        print "WARNING: An error occured when trying to send the text to Slack."

    ## outputs to command line so you can follow along/log there, especially when working locally
    print text