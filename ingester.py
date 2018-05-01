import json
import os
import requests

from datetime import datetime
from prometheus_client import start_http_server, Counter
from requests.auth import HTTPBasicAuth
from twisted.internet import reactor, task
from twisted.python import log

MAILCHIMP_API_KEY_ENV = 'MAILCHIMP_API_KEY'
OMETRIA_API_KEY_ENV = 'OMETRIA_API_KEY'
MAIL_LIST_ID_ENV = "MAILCHIMP_LIST_ID"
DEFAULT_SYNC_TIME = 60 * 60  # Sync every hour

# Catch and report errors in a usuable fashion.
mc_failures = Counter('mailchimp_failures_total', 'Number of mailchimp request failures')
om_failures = Counter('ometria_failures_total', 'Number of ometria request failures')

MAIL_CHIMP_URL = "https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members"
OMETRIA_API_URL = " http://ec2-34-242-147-110.eu-west-1.compute.amazonaws.com:8080/record"


# Take a mailchimp response and format it to a valid ometria one.
def transform_data(list_id, data):
    output = []
    if 'members' not in data:
        # TODO: raise exception, malformed data or something...
        return output
    for member in data['members']:
        record = {"id": list_id,  # Wasn't sure if this was the correct ID
                  "firstname": member['merge_fields']['FNAME'],
                  "lastname": member['merge_fields']['LNAME'],
                  "email": member['email_address']}
        output.append(record)
    return output


class IntermediateController:
    def __init__(self, mc_key, om_key, list_id, last_successfull=None):
        self.mc_api_key = mc_key
        self.om_api_key = om_key
        # Get the mailchimp DC from the API key
        self.mc_dc = mc_key.split("-")[-1]  # A bit hacky but will do for now.
        self.list_id = list_id
        self.last_successfull = last_successfull  # Query from a given date

    @mc_failures.count_exceptions()
    def query_mailchimp(self, from_time=""):
        print("Querying mailchimp")
        if (from_time == "") and self.last_successfull:
            from_time = self.last_successfull.isoformat()
        # Do a simple time based query on mailchimp to sync with
        url = MAIL_CHIMP_URL.format(dc=self.mc_dc, list_id=self.list_id)
        auth = HTTPBasicAuth('bananas-are-cool', self.mc_api_key)
        params = None
        if from_time != "":
            params = {'since_last_changed': from_time}
        resp = requests.get(url, auth=auth, params=params)
        if not resp.ok:
            print(resp.reason)
        resp.raise_for_status()
        return json.loads(resp.text)

    @om_failures.count_exceptions()
    def update_ometria(self, data):
        print("Updating ometria database")
        headers = {'content-type': 'application/json',
                   'Authorization': self.om_api_key}  # Damn Americans...
        resp = requests.post(OMETRIA_API_URL, data=data, headers=headers)
        print(resp.text)
        resp.raise_for_status()
        # Update from time since successfull
        self.last_successfull = datetime.now()

    def run(self):
        data = self.query_mailchimp()
        data = transform_data(self.list_id, data)
        if len(data) == 0:
            print("No data found")
            return
        self.update_ometria(json.dumps(data))


if __name__ == '__main__':
    # Read configuration from enviroment variables.
    mailchimp_api_key = ""
    ometria_api_key = ""
    list_id = ""
    if MAILCHIMP_API_KEY_ENV in os.environ:
        mailchimp_api_key = os.environ[MAILCHIMP_API_KEY_ENV]
    if MAILCHIMP_API_KEY_ENV in os.environ:
        ometria_api_key = os.environ[OMETRIA_API_KEY_ENV]
    if MAIL_LIST_ID_ENV in os.environ:
        list_id = os.environ[MAIL_LIST_ID_ENV]
    # TODO: check if empty, exit if not set. maybe read defaults from somewhere?
    # Start Prometheus metrics for reporting
    start_http_server(8888)

    # Create new controller and run sync every N seconds
    i = IntermediateController(mailchimp_api_key, ometria_api_key, list_id)
    # Loop forever
    # Could start multiple of these hand have twisted run them at arbitatry times
    loop = task.LoopingCall(i.run)
    loop.start(DEFAULT_SYNC_TIME).addErrback(log.err)
    reactor.run()
