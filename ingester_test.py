import unittest
import ingester

sample_input = {"members": [
                {"merge_fields": {"FNAME": "Tom", "LNAME": "Vass"},
                 "email_address": "mr.tom.vass@gmail.com"}]
                }

sample_list_id = "lemons"


class IngesterTest(unittest.TestCase):

    def test_transform(self):
        output = ingester.transform_data(sample_list_id, sample_input)
        self.assertEqual(len(output), 1)


if __name__ == '__main__':
    unittest.main()
