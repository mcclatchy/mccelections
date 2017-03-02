## NOTE: if activated here, remove from models
# from django.db.models.signals import post_save 
# from django.dispatch import receiver
## doesn't work
# from .models import ResultManual


""" ReportingUnit """

## update related ResultManual object after ReportingUnit save
# @receiver(post_save, sender=ReportingUnit, dispatch_uid="update_related_result_manual")
# def calculate_vote(sender, instance, **kwargs):
#     call_command('sync_precinctsreporting')

""" ResultManual """

# ## calculate votes
# @receiver(post_save, sender=ResultManual, dispatch_uid="call_calculate_vote_command")
# def calculate_vote(sender, instance, **kwargs):
#     ## don't fire if it's a gdoc result
#     if instance.gdoc_import != True:
#         electiondate_arg = str(instance.electiondate)
#         call_command('calculate_vote', electiondate_arg)
#         ## needs to be written <-- not doing this bc it would mess with manual results w/ multiple winners, winners that req 2/3, etc
#         # call_command('declare_winner')

## ARE THESE EVEN THE RIGHT WAY TO DO THESE? Maybe not... reconsider

## update precinctsreportingpct from ReportingUnit on ResultManual
    ## trigger a save() of ResultManual each time ReportingUnit is saved?
    ## or just a post_save signal
# @receiver(post_save, sender=ReportingUnit, dispatch_uid="update_precinctsreportingpct_on_resultmanual")
# def update_resultmanual_from_reporting_unit(sender, instance, **kwargs):
    # 

## update race_type and is_ballot_measure from Race on ResultManual

# @receiver(post_save, sender=Race, dispatch_uid="update_is_ballot_measure_on_resultmanual")
# def update_is_ballot_measure_on_resultmanual(sender, instance, **kwargs):
    # 

# @receiver(post_save, sender=Race, dispatch_uid="update_racetype_on_resultmanual")
# def update_race_type_on_resultmanual(sender, instance, **kwargs):
    # 

""" Embed """

## post_save method to re-save embed on save so users don't have to save twice to see embed code updates after changing races
# @receiver(post_save, sender=Embed, dispatch_uid="save_embed")
# def save_embed(sender, instance, **kwargs):
#     from results.slackbot import slackbot

#     now = timezone.localtime(timezone.now())
#     slackbot(now)
#     time_difference = now - timedelta(seconds=15)
#     if time_difference < instance.systemupdated: 
#         id_arg = str(instance.id)
#         slackbot(id_arg)
#         call_command('save_embed', id_arg)
#         slackbot("command called")
    # instance.update()