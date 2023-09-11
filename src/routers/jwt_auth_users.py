from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from redis_client.crud import get_user
from schemas.user_schema import get_user_schema
from datetime import datetime, timedelta
from models.users.user import *

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "7d72bbf2561d018343b5101d1c50db5a96cee3e9fda2ef23128821f9e0e0cca7"  # openssl rand -hex 32

router_jwt = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth2/login")
crypt = CryptContext(schemes=["bcrypt"])


def verify_password(plain_password, hashed_password):
    return crypt.verify(plain_password, hashed_password)


def get_password_hash(password):
    return crypt.hash(password)


async def auth_user(token: str = Depends(oauth2)):
    try:
        user_id = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("sub")
        if user_id is None:
            raise JWTError
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not valid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = get_user(str(user_id))
    return User(**get_user_schema(user))


async def current_user(user: User = Depends(auth_user)):
    if not user.is_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not activated"
        )
    return user


async def role_current_user(user: User = Depends(current_user)):
    if Role.admin not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid privileges, admin role is required"
        )
    return user


@router_jwt.post("/oauth2/login", description="Username reference to the user id", tags=["oauth2"])
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if not get_user(form.username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {form.username} does not exist")

    user = UserDB(**get_user_schema(get_user(form.username)))

    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The password is incorrect")

    # It calculates the token expiration
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = {"sub": str(user.id),
                    "exp": expire}
    return {"access_token": jwt.encode(access_token, key=SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}


@router_jwt.get(path="/users/my-user/", response_model=User, tags=["users"])
async def me(user: User = Depends(current_user)):
    return user
