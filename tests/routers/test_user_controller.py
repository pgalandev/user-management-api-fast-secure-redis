import unittest
from unittest.mock import patch, Mock

from src.models.users.user import Role, Gender
from src.routers.users_controller import (UUID, get, create_user)


class TestUserController(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.mocked_response = {
            "id": "f01797e9-4c6d-4e81-ac98-3db79bb29b32",
            "first_name": "Test",
            "last_name": "2",
            "gender": "male",
            "roles": ["user"],
            "activated_at": 0,
            "is_activated": True,
            "updated_at": 0,
            "entity_type": "User",
            "in_charge": set(),
            "managed_by": None,
            "hashed_password": "e"
        }

    @patch('src.services.users_service.process_get_user')
    async def test_get_request(self, mock_get: Mock):
        mock_get.return_value = self.mocked_response

        response = await get(UUID("f01797e9-4c6d-4e81-ac98-3db79bb29b32"))
        self.assertTrue(response.success)
        self.assertEqual("Data found", response.message)
        self.assertEqual(UUID("f01797e9-4c6d-4e81-ac98-3db79bb29b32"), response.data.id)

    @patch('src.services.users_service.process_create_user')
    async def test_post_user(self, mock_get: Mock):
        mock_get.return_value = self.mocked_response

        response = await create_user(user_id=UUID("f01797e9-4c6d-4e81-ac98-3db79bb29b32"), first_name="Test",
                                     gender=Gender.male, roles=[Role.user], password="test")
        self.assertTrue(response.success)
        self.assertEqual("User f01797e9-4c6d-4e81-ac98-3db79bb29b32 created successfully", response.message)
        self.assertEqual(UUID("f01797e9-4c6d-4e81-ac98-3db79bb29b32"), response.data.id)
