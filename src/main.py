"""
Initiate fastapi app and its routers
"""


from fastapi import FastAPI, Depends
from src.routers.users_controller import router_user
from src.routers.jwt_auth_users import router_jwt, current_user

API_VERSION = "/api/v1"

app = FastAPI()

app.include_router(router_user, prefix=API_VERSION, tags=["users"], dependencies=[Depends(current_user)])
app.include_router(router_jwt, prefix=API_VERSION)
