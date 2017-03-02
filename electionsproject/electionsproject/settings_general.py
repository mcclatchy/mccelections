## general results app vars
import os


## S3 acces keys
S3_ACCESS_KEY = os.environ['S3_ACCESS_KEY']
S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
S3_BUCKET = os.environ['S3_BUCKET']

## AP embed - models.py
AP_EMBED_BASE_URL = "http://hosted.ap.org/elections/2016/general/by_race/" ## always ends with trailing slash: /

SITE_ID = "<YOUR_SITE_ID>"

## import frequency - election_auto.py
RESULTSTAGE_IMPORT_SLEEP_TIME = "60"

