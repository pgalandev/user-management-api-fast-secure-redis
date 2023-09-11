import logging

from redis_client.crud import set_user, get_user, ResponseError, get_all_users_db
from models.users.user import *
from schemas.user_schema import get_user_schema, get_users_schema
from fastapi import HTTPException, status
from routers.jwt_auth_users import get_password_hash


async def create_user(first_name: str,
                      gender: Gender,
                      roles: List[Role],
                      password: str,
                      in_charge: Optional[Set[UUID]],
                      managed_by: Optional[UUID],
                      user_id: Optional[UUID],
                      last_name: Optional[str]) -> dict:
    if user_id and get_user(str(user_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already created")
    try:

        user = UserDB(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            roles=roles,
            in_charge=in_charge,
            managed_by=managed_by,
            hashed_password=get_password_hash(password)
        )
        if user.managed_by:
            manager = UserDB(**get_user_schema(get_user(str(user.managed_by))))
            if not manager:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Manager with id= {user.managed_by} does not exist")
            elif Role.manager not in manager.roles and Role.admin not in manager.roles:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Invalid manager with id= {user.managed_by} for user with id={user.id}")
            else:
                # Creating the new user
                set_user(str(user.id), user.model_dump_json())
                # Updating users set managed by the manager
                manager.in_charge.add(user.id)
                set_user(str(manager.id), manager.model_dump_json())

        else:
            # Creating the new user not managed
            set_user(str(user.id), user.model_dump_json())

    except ValueError as value_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ERROR: {value_error}")

    except ResponseError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}, "
                                                                                      f"the user may not have been "
                                                                                      f"created properly")
    else:
        return get_user_schema(get_user(str(user.id)))


async def get_all_users(total_number: Optional[int]) -> List[object]:
    try:
        users = get_all_users_db(total_number)
        if not users:
            return list()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}")

    return get_users_schema(users, UserResponse)


async def update_user(user_id: UUID,
                      first_name: str,
                      gender: Gender,
                      roles: List[Role],
                      in_charge: Optional[List[UUID]],
                      managed_by: Optional[UUID],
                      last_name: Optional[str]) -> dict:
    user_id = str(user_id)
    try:
        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id={user_id} not found")

        outdated_user = UserDB(**get_user_schema(user))
        updated_user = UserDB(id=user_id,
                              first_name=first_name,
                              last_name=last_name,
                              gender=gender,
                              roles=roles,
                              in_charge=in_charge,
                              managed_by=managed_by,
                              activated_at=outdated_user.activated_at,
                              updated_at=time_ns(),
                              hashed_password=outdated_user.hashed_password)

        # TODO update checkers

        # Update
        set_user(user_id, updated_user.model_dump_json())

    except ValueError as validation_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ERROR: {validation_error}")

    except ResponseError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}, "
                                                                                      f"the user may not have been "
                                                                                      f"updated properly")

    return get_user_schema(get_user(user_id))


def __user_update_check(outdated_user: User, updated_user: User):
    pass
