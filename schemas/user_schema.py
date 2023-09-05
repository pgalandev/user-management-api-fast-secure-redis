from models.user import User, List


def get_user_schema(user) -> dict:
    return {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "gender": user["gender"],
        "roles": user["roles"],
        "activated_at": user["activated_at"],
        "is_activated": user["is_activated"],
        "updated_at": user["updated_at"],
        "entity_type": user["entity_type"],
        "hashed_password": user["hashed_password"]
    }


def get_users_schema(users) -> List[User]:
    return [User(**get_user_schema(user)) for user in users]
