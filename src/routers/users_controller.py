from fastapi import APIRouter, HTTPException, status, Depends
from redis_client.crud import get_user, set_user, get_all_users_db, delete_user, delete_all_users, ResponseError
from schemas.user_schema import get_user_schema
from models.users.user import *
from routers.jwt_auth_users import role_current_user
from services import users_service

router_user = APIRouter()


@router_user.post(path="/users/bulk", response_model=UserResponse,
                  status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_current_user)])
async def create_user_bulk(user: UserDTO):
    user_created = await users_service.create_user(
        user_id=user.id, first_name=user.first_name, last_name=user.last_name, gender=user.gender,
        roles=user.roles, in_charge=user.in_charge, managed_by=user.managed_by, password=user.password)

    return UserDTO(**user_created, password=user.password)


@router_user.post(path="/users", response_model=UserDTO,
                  status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_current_user)])
async def create_user(
        first_name: str,
        gender: Gender,
        roles: List[Role],
        password: str,
        in_charge: Optional[Set[UUID]] = None,
        managed_by: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        last_name: Optional[str] = None):
    user_created = await users_service.create_user(user_id=user_id, first_name=first_name, last_name=last_name,
                                                   gender=gender,
                                                   roles=roles, in_charge=in_charge, managed_by=managed_by,
                                                   password=password)

    return UserDTO(**user_created, password=password)


@router_user.get(path="/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_all(total_number: Optional[int] = None):
    return await users_service.get_all_users_db(total_number)


@router_user.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get(user_id: UUID):
    user_id = str(user_id)
    try:
        user = get_user(user_id)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}")

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id={user_id} not found")
    return User(**get_user_schema(user))


@router_user.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def put(user_id: UUID,
              first_name: str,
              gender: Gender,
              roles: List[Role],
              in_charge: Optional[List[UUID]] = None,
              managed_by: Optional[UUID] = None,
              last_name: Optional[str] = None):

    updated_user = await users_service.update_user(user_id=user_id, first_name=first_name, gender=gender, roles=roles,
                                                   in_charge=in_charge, managed_by=managed_by, last_name=last_name)

    return UserResponse(**dict(updated_user))


@router_user.patch("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def patch(user_id: UUID,
                first_name: str = None,
                last_name: str = None,
                gender: Gender = None,
                roles: List[Role] = None):
    user_id = str(user_id)
    try:
        user = get_user_schema(get_user(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id={user_id} not found")

        if not first_name and not last_name and not gender and not roles:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No field modified")

        updated_user = UserDB(id=user_id,
                              first_name=first_name if first_name else user["first_name"],
                              last_name=last_name if last_name else user["last_name"],
                              gender=gender if gender else user["gender"],
                              roles=roles if roles else user["roles"],
                              activated_at=user["activated_at"],
                              updated_at=time_ns())

        # Update
        set_user(user_id, updated_user.model_dump_json())

    except ResponseError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}, the user "
                                                                                      f"may not have been patched "
                                                                                      f"properly")

    return User(**dict(updated_user))


@router_user.delete("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def delete(user_id: UUID):
    user_id = str(user_id)
    try:
        user = get_user_schema(get_user(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id={user_id} not found")

        delete_user(user_id)
    except ResponseError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}, the user "
                                                                                      f"may not have been deleted")

    return User(**user)


@router_user.delete("/users", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all():
    try:
        delete_all_users()
    except ResponseError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ERROR: {error.args}, "
                                                                                      f"the users may not have been "
                                                                                      f"deleted")
