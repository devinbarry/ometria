import unittest
from unittest import mock
from unittest.mock import MagicMock
from datetime import datetime
from ingest.ingester import MailchimpAPIImporter
from ingest.exceptions import MailchimpAPIImporterException

missing_fields = {
    'members': [{'merge_fields': {'FNAME': 'Tom', 'LNAME': 'Vass'}, 'email_address': 'mr.tom.vass@gmail.com'}]
}

complete_data = {
    'members': [{
        'unique_email_id': '6dbc8af3a7',
        'email_address': 'mr.tom.vass@gmail.com',
        'status': 'subscribed',
        'merge_fields': {
            'FNAME': 'Tom', 'LNAME': 'Vass'
        },
    }]
}


class MockRequests(MagicMock):

    def get(self, **kwargs):
        response = MagicMock()
        response.json.return_value = complete_data
        return response

    def post(self, **kwargs):
        response = MagicMock()
        response.json.return_value = {"content": 1, "status": "OK"}
        return response


class MockOmetriaEmpty(MockRequests):

    def post(self, **kwargs):
        response = MagicMock()
        response.json.return_value = {"content": 0, "status": "OK"}
        return response


class IngesterTransformTest(unittest.TestCase):

    def test_invalid_response_mailchimp(self):
        importer = MailchimpAPIImporter(mc_key='', om_key='')
        with self.assertRaises(MailchimpAPIImporterException):
            importer.transform_data({'not members': [1, 2, 3, 4]})

    def test_missing_keys(self):
        # Should not raise exception
        importer = MailchimpAPIImporter(mc_key='', om_key='')
        output = importer.transform_data(missing_fields)
        self.assertEqual(output, [])

    def test_transform(self):
        importer = MailchimpAPIImporter(mc_key='', om_key='')
        output = importer.transform_data(complete_data)
        self.assertEqual(len(output), 1)


class IngesterTest(unittest.TestCase):

    @mock.patch('ingest.ingester.requests', new=MockOmetriaEmpty)
    def test_ometria_failed_update(self):
        # Test the Importer
        importer = MailchimpAPIImporter(mc_key='', om_key='')
        self.assertIsNone(importer.last_successful)

        with self.assertRaises(MailchimpAPIImporterException) as ar:
            importer.run()

        # Check exception message matches
        self.assertIn('Unable to save all contacts to Ometria', str(ar.exception))

        # last_successful should still be None because we didn't update correctly
        self.assertIsNone(importer.last_successful)

    @mock.patch('ingest.ingester.requests', new=MockRequests)
    def test_ometria_correct_update(self):
        start_time = datetime.now()
        importer = MailchimpAPIImporter(mc_key='', om_key='')
        self.assertIsNone(importer.last_successful)
        importer.run()
        # last_successful is now set to the current time because run was successful
        self.assertIsInstance(importer.last_successful, datetime)
        self.assertGreater(importer.last_successful, start_time)


if __name__ == '__main__':
    unittest.main()
