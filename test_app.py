import unittest
from app import cypher_string, decode

class AppTest(unittest.TestCase):
    def test_cypher_string_escapes_quotes_and_slashes(self):
        self.assertEqual(cypher_string("A\\B's"), "'A\\\\B\\'s'")

    def test_decode_typed_hydra_values(self):
        self.assertEqual(decode({"type": "string", "value": "quiet"}), "quiet")
        self.assertEqual(decode({"nested": {"type": "boolean", "value": True}}), {"nested": True})

if __name__ == "__main__": unittest.main()
