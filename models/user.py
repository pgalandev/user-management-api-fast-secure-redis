from time import time_ns
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    combat_helicopter = "combat_helicopter"


class Role(str, Enum):
    user = "user"
    admin = "admin"


class User(BaseModel):
    id: Optional[UUID] = uuid4()
    first_name: str
    last_name: Optional[str] = None
    gender: Gender
    roles: List[Role]
    is_activated: bool = True
    activated_at: int = time_ns()  # timestamp
    updated_at: Optional[int] = None  # timestamp
    entity_type: str = "User"


class UserCreationResponse(User):
    plain_password: str


class UserDB(User):
    hashed_password: str
