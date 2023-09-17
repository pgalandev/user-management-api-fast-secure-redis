import unittest
from uuid import UUID
from src.models.users.user import User


class TestUser(unittest.TestCase):

    def setUp(self) -> None:
        self.user1 = User(id="f01797e9-4c6d-4e81-ac98-3db79bb29b32", first_name="Test1", gender="male", roles=["user"])
        self.user2 = User(first_name="Test2", gender="female", roles=["manager"], in_charge=[self.user1.id])

    def test_basic(self):
        self.assertEqual("Test1", self.user1.first_name)
        self.assertIs(type(self.user2.id), UUID)
        self.assertTrue(self.user2.is_activated)

    def test_validation(self):
        self.assertIn(UUID("f01797e9-4c6d-4e81-ac98-3db79bb29b32"), self.user2.in_charge)
        with self.assertRaises(ValueError):
            User(id="1", first_name="Test1", gender="male", roles=["user"])
        with self.assertRaises(ValueError):
            User(first_name="Test1", gender="male", roles=["user"], in_charge=["f01797e9-4c6d-4e81-ac98-3db79bb29b32"])
        with self.assertRaises(ValueError):
            User(first_name="Test1", gender="male", is_activated=False, roles=["manager"],
                 in_charge=["f01797e9-4c6d-4e81-ac98-3db79bb29b32"])

