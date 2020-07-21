from quantum_lamps import clean_incoming_data
import json
import unittest


class TestMessageHandler(unittest.TestCase):
    
    def test_clean_incoming_data_test(self):
        x = 255
        y = 255
        z = 0
        correct_message = json.dumps({'type': 'Input', 'payload': [x, y, z]})
        expected_result = [int(x), int(y), int(z)]
        result = clean_incoming_data(correct_message)
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
