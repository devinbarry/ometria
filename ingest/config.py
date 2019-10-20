import os

MAILCHIMP_API_KEY_ENV = 'MAILCHIMP_API_KEY'
OMETRIA_API_KEY_ENV = 'OMETRIA_API_KEY'
MAIL_LIST_ID_ENV = "MAILCHIMP_LIST_ID"

MAILCHIMP_API_KEY = os.environ.get(MAILCHIMP_API_KEY_ENV)
OMETRIA_API_KEY = os.environ.get(OMETRIA_API_KEY_ENV)
MAIL_LIST_ID = os.environ.get(MAIL_LIST_ID_ENV)
DEFAULT_SYNC_TIME = 60 * 60  # seconds

# Get the mailchimp DC from the API key
assert "-" in MAILCHIMP_API_KEY
MAIL_CHIMP_DC = MAILCHIMP_API_KEY.split("-")[-1]  # A bit hacky but will do for now.

MAIL_CHIMP_URL = f"https://{MAIL_CHIMP_DC}.api.mailchimp.com/3.0/lists/{MAIL_LIST_ID}/members"
OMETRIA_API_URL = "http://ec2-34-242-147-110.eu-west-1.compute.amazonaws.com:8080/record"
