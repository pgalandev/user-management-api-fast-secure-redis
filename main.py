from fastapi import FastAPI, Depends
from routers.users_controller import router_user
from routers.jwt_auth_users import router_jwt, current_user

USERS_ENDPOINT_PATH = "/api/v1/users"

app = FastAPI()

app.include_router(router_user, prefix=USERS_ENDPOINT_PATH, tags=["users"], dependencies=[Depends(current_user)])
app.include_router(router_jwt, prefix=USERS_ENDPOINT_PATH, tags=["users"])

