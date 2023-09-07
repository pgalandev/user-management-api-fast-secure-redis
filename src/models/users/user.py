from time import time_ns
from pydantic import (BaseModel, model_validator)
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
    manager = "manager"


class User(BaseModel):
    id: Optional[UUID] = uuid4()
    first_name: str
    last_name: Optional[str] = None
    gender: Gender
    roles: List[Role]
    is_activated: bool = True
    activated_at: int = time_ns()  # timestamp
    updated_at: Optional[int] = None  # timestamp
    in_charge: List[UUID] = []
    managed_by: Optional[UUID] = None
    entity_type: str = "User"

    @model_validator(mode='after')
    def __in_charge_validator(self) -> 'User':
        if self.in_charge:
            if not self.is_activated:
                raise ValueError(f'User {self.first_name} is not activated')
            if Role.manager not in self.roles:
                raise ValueError(f'User {self.first_name} is not manager')
        return self


class UserCreation(User):
    plain_password: str


class UserDB(User):
    hashed_password: str
