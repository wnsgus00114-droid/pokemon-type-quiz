import tempfile
import unittest
from pathlib import Path

import database


class PartnerPersistenceTest(unittest.TestCase):
    def setUp(self):
        self.original_path = database.DB_PATH
        self.tempdir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.tempdir.name) / "test.db"
        database.initialize_database()

    def tearDown(self):
        database.DB_PATH = self.original_path
        self.tempdir.cleanup()

    def test_partner_is_granted_once_and_persists(self):
        created, _ = database.create_user("test_trainer", "trainer2026")
        self.assertTrue(created)
        user = database.authenticate("test_trainer", "trainer2026")
        self.assertIsNone(user["partner_pokemon"])

        granted = database.grant_partner_pokemon(user["id"])
        self.assertEqual(granted, "루미볼트")
        self.assertEqual(database.get_user(user["id"])["partner_pokemon"], "루미볼트")

        # A later grant request cannot replace the original partner.
        granted_again = database.grant_partner_pokemon(user["id"], "다른몬")
        self.assertEqual(granted_again, "루미볼트")


if __name__ == "__main__":
    unittest.main()
