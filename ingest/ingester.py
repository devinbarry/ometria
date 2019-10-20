import json
import logging
import requests

from datetime import datetime
from prometheus_client import Counter
from requests.auth import HTTPBasicAuth

from .exceptions import MailchimpAPIImporterException
from .config import MAIL_CHIMP_URL, OMETRIA_API_URL


logger = logging.getLogger(__name__)


# Catch and report errors in a usuable fashion.
mc_failures = Counter('mailchimp_failures_total', 'Number of mailchimp request failures')
om_failures = Counter('ometria_failures_total', 'Number of ometria request failures')


class MailchimpAPIImporter:

    # Fields to fetch from Mailchimp
    FIELDS = ('members.email_address', 'members.unique_email_id', 'members.status', 'members.merge_fields.FNAME',
              'members.merge_fields.LNAME')

    def __init__(self, mc_key, om_key, last_successful=None):
        self.mc_url = MAIL_CHIMP_URL
        self.mc_api_key = mc_key
        self.om_api_key = om_key
        self.last_successful = last_successful  # Query from a given date

    @mc_failures.count_exceptions()
    def query_mailchimp(self, from_time=None):
        params = {'fields': ','.join(self.FIELDS)}

        if not from_time and self.last_successful:
            from_time = self.last_successful.isoformat()
        if from_time:
            params.update({'since_last_changed': from_time})

        # Make the request to Mailchimp
        auth = HTTPBasicAuth('bananas-are-cool', self.mc_api_key)
        resp = requests.get(self.mc_url, auth=auth, params=params)

        if not resp.ok:
            logger.error(f"[{resp.status_code}] received from MailChimp: {resp.reason}")
        resp.raise_for_status()

        return resp.json()

    @staticmethod
    def transform_data(data):
        """
        Convert MailChimp response and format it to a valid Ometria contact record.
        :return:
        """
        output = []
        if 'members' not in data:
            raise MailchimpAPIImporterException(f"Invalid response from Mailchimp: {data}")

        for member in data['members']:
            print(member)
            try:
                record = {
                    "id": member['unique_email_id'],
                    "firstname": member['merge_fields']['FNAME'],
                    "lastname": member['merge_fields']['LNAME'],
                    "email": member['email_address'],
                    "status": member['status'],
                }
            except KeyError as e:
                # Skip this record, it is malformed
                logger.warning(e)
            else:
                output.append(record)
        # Format to JSON string to send to Ometria API
        return json.dumps(output)

    @om_failures.count_exceptions()
    def update_ometria(self, data: str):
        logger.info("Updating Ometria database")
        headers = {'content-type': 'application/json', 'Authorisation': self.om_api_key}
        resp = requests.post(OMETRIA_API_URL, data=data, headers=headers)
        logger.info(resp.text)
        resp.raise_for_status()
        # Update from time since successful
        self.last_successful = datetime.now()

    def run(self):
        logger.info(f"Querying mailchimp: {self.mc_url}")
        data = self.query_mailchimp()

        if len(data) == 0:
            logger.info("No new data available from MailChimp")
            return

        self.update_ometria(self.transform_data(data))
