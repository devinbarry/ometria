import unittest
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


class IngesterTest(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
