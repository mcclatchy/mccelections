from django.core.management import call_command
from slackbot import slackbot
## for core schedule pieces
import schedule
import time
## for catching exceptions
# import functools


## to catch exceptions, add decorator -- defined here -- to functions: @catch_exceptions
# def catch_exceptions(job_func):
#     @functools.wraps(job_func)
#     def wrapper(*args, **kwargs):
#         try:
#             job_func(*args, **kwargs)
#         except:
#             import traceback
#             print(traceback.format_exc())
#     return wrapper


## NOTE: how to run this module? cron? every minute? doesn't seem like it
## if it's just a module with a bunch of functions running on cron, then what's the point of even using the 'schedule' module?

'''
tasks
'''
def test():
    message = "This is just a test..."
    slackbot(message)

## import new AP elections, if any
def download_elections():
    call_command('download_elections')

## check if there's an Election today; if so, start checking every minute whether to set live and start import
def election_auto():
    call_command('election_auto')

'''
schedule
'''
schedule.every(10).seconds.do(test)
schedule.every(1).day.at("6:00").do(download_elections)
schedule.every(1).day.at("12:00").do(election_auto)

# def minute_jobs():
    ## should this just be called through another function that's triggered on election day?
    # call_command('election_set_live_true')

# def daily_jobs():


## really need to save this somewhere that's not on the server bc they'll pile up quickly!
#     ## https://docs.djangoproject.com/en/1.9/ref/django-admin/#dumpdata
#     # ./manage.py dumpdata > ~/mccelectionsbackup/mccelectionsYYYYMMDD.json
#     ## use stdout method?
#       ## https://docs.djangoproject.com/en/1.9/ref/django-admin/#output-redirection
        ## http://stackoverflow.com/a/20480323/217955
#    call_command('dumpdata') 

# def job_that_executes_once():
#     ## loads candidates, races, results
#     # load_data_all()
#     print "Testing run once..."
#     return schedule.CancelJob

# starttime_time = # pull out the time from Election starttime field?
# daily_job_time = "5:00"

## EXAMPLES
# schedule.every(1).minutes.do(minute_jobs)
# schedule.every(1).day.at(daily_job_time).do(daily_jobs)
# schedule.every(10).seconds.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every(1).minutes.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().day.at(start_time_time).do(job)
# schedule.every().monday.at("20:30").do(job_that_executes_once)

while True:
    schedule.run_pending()
    time.sleep(1) # 1 sec
    # time.sleep(60) # 1 min