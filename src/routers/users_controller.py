from fastapi import APIRouter, HTTPException, status, Depends
from src.models.users.user import *
from src.routers.jwt_auth_users import role_current_user
from src.services import users_service
from src.models.responses.api_response import ApiResponse

router_user = APIRouter()


@router_user.post(path="/users/bulk", response_model=ApiResponse, response_description="User created successfully",
                  status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_current_user)])
async def create_user_bulk(user: UserDTO) -> ApiResponse:
    user_created = await users_service.process_create_user(first_name=user.first_name, gender=user.gender,
                                                           roles=user.roles, password=user.password,
                                                           in_charge=user.in_charge, managed_by=user.managed_by,
                                                           user_id=user.id, last_name=user.last_name)

    return ApiResponse(success=True,
                       message=f"User {user_created['id']} created successfully",
                       data=UserResponse(**user_created))


@router_user.post(path="/users", response_model=ApiResponse, response_description="User created successfully",
                  status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_current_user)])
async def create_user(
        first_name: str,
        gender: Gender,
        roles: List[Role],
        password: str,
        in_charge: Optional[Set[UUID]] = None,
        managed_by: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        last_name: Optional[str] = None) -> ApiResponse:
    user_created = await users_service.process_create_user(first_name=first_name, gender=gender, roles=roles,
                                                           password=password, in_charge=in_charge,
                                                           managed_by=managed_by, user_id=user_id, last_name=last_name)

    return ApiResponse(success=True,
                       message=f"User {user_created['id']} created successfully",
                       data=UserResponse(**user_created))


@router_user.get(path="/users", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def get_all(total_number: Optional[int] = None) -> ApiResponse:
    return ApiResponse(success=True, message="Data found", data=await users_service.process_get_all_users(total_number))


@router_user.get("/users/{user_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def get(user_id: UUID) -> ApiResponse:
    return ApiResponse(success=True,
                       message="Data found",
                       data=UserResponse(**await users_service.process_get_user(user_id)))


@router_user.put(path="/users/{user_id}", response_model=ApiResponse,
                 response_description="User updated successfully",
                 status_code=status.HTTP_200_OK, dependencies=[Depends(role_current_user)])
async def put(user_id: UUID,
              first_name: str,
              gender: Gender,
              roles: List[Role],
              password: str,
              in_charge: Optional[List[UUID]] = None,
              managed_by: Optional[UUID] = None,
              last_name: Optional[str] = None) -> ApiResponse:
    updated_user = await users_service.process_update_user(user_id=user_id, first_name=first_name,
                                                           gender=gender, roles=roles,
                                                           in_charge=in_charge, managed_by=managed_by,
                                                           last_name=last_name, password=password)

    return ApiResponse(success=True,
                       message=f"User {user_id} updated",
                       data=UserResponse(**updated_user))


@router_user.put(path="/users/{user_id}/bulk", response_model=UserResponse,
                 response_description="User updated successfully",
                 status_code=status.HTTP_200_OK, dependencies=[Depends(role_current_user)])
async def put_bulk(user: UserDTO) -> ApiResponse:
    updated_user = await users_service.process_update_user(user_id=user.id, first_name=user.first_name,
                                                           gender=user.gender, roles=user.roles,
                                                           in_charge=user.in_charge, managed_by=user.managed_by,
                                                           last_name=user.last_name, password=user.password)

    return ApiResponse(success=True,
                       message=f"User {user.id} updated",
                       data=UserResponse(**updated_user))


@router_user.patch(path="/users/{user_id}", response_model=ApiResponse,
                   response_description="User patched successfully", status_code=status.HTTP_200_OK,
                   dependencies=[Depends(role_current_user)])
async def patch_user(user_id: UUID,
                     first_name: Optional[str] = None,
                     last_name: Optional[str] = None,
                     gender: Optional[Gender] = None,
                     roles: Optional[List[Role]] = None,
                     password: Optional[str] = None,
                     managed_by: Optional[UUID] = None,
                     in_charge: Optional[Set[UUID]] = None) -> ApiResponse:
    if (not first_name and not last_name and not gender and not roles and
            not managed_by and in_charge is None and not password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No field modified")

    patched_user = await users_service.process_patch_user(user_id=user_id, first_name=first_name, last_name=last_name,
                                                          gender=gender, roles=roles, managed_by=managed_by,
                                                          in_charge=in_charge, password=password)
    return ApiResponse(success=True,
                       message=f"User {user_id} patched",
                       data=UserResponse(**patched_user))


@router_user.delete(path="/users/{user_id}", response_model=ApiResponse,
                    response_description="User deleted successfully",
                    status_code=status.HTTP_200_OK, dependencies=[Depends(role_current_user)])
async def delete(user_id: UUID) -> ApiResponse:
    deleted_user = await users_service.process_delete_user(user_id)
    return ApiResponse(success=True,
                       message=f"User {user_id} deleted successfully",
                       data=UserResponse(**deleted_user))


@router_user.delete(path="/users", status_code=status.HTTP_200_OK, response_model=ApiResponse,
                    response_description="All users deleted successfully", dependencies=[Depends(role_current_user)])
async def delete_all() -> ApiResponse:
    await users_service.process_delete_all_users()
    return ApiResponse(success=True, message="All users have been deleted successfully")


@router_user.get(path="/users/{user_id}/managed_users", description="Retrieve all subordinates by a manager",
                 response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def get_managed_users(user_id: UUID):
    subordinates = await users_service.process_get_managed_users(user_id)
    if not subordinates:
        return ApiResponse(
            success=False,
            message=f"No users managed by {user_id} found",
            data={
                "subordinates_count": len(subordinates),
                "data": subordinates
            }
        )
    logging.info(subordinates)
    return ApiResponse(
        success=True,
        message="Data found",
        data={
            "subordinates_count": len(subordinates),
            "data": subordinates
        }
    )


@router_user.post(path="/users/{user_id}/managed_users", status_code=status.HTTP_201_CREATED,
                  response_model=ApiResponse, description="Add a subordinate to the manager's in_charge set",
                  response_description="Subordinate added successfully", dependencies=[Depends(role_current_user)])
async def post_subordinates(user_id: UUID, subordinate_id: UUID) -> ApiResponse:
    subordinates = await users_service.process_add_subordinate(manager_id=user_id, subordinate_id=subordinate_id)
    return ApiResponse(
        success=True,
        message=f"Subordinate {subordinate_id} added to manager's ({user_id}) in_charge set successfully",
        data={
            "subordinates_count": len(subordinates),
            "data": subordinates
        }
    )


@router_user.delete(path="/users/{user_id}/managed_users/{subordinate_id}", status_code=status.HTTP_201_CREATED,
                    response_model=ApiResponse, description="Delete a subordinate from the manager's in_charge set",
                    response_description="Subordinate deleted successfully", dependencies=[Depends(role_current_user)])
async def delete_subordinate(user_id: UUID, subordinate_id: UUID) -> ApiResponse:
    subordinates = await users_service.process_delete_subordinate(manager_id=user_id, subordinate_id=subordinate_id)
    return ApiResponse(
        success=True,
        message=f"Subordinate {subordinate_id} deleted from manager's ({user_id}) in_charge set successfully",
        data={
            "subordinates_count": len(subordinates),
            "data": subordinates
        }
    )
