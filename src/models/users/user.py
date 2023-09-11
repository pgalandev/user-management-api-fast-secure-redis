import logging
from time import time_ns
from pydantic import (BaseModel, model_validator, field_validator)
from uuid import UUID, uuid4
from typing import Optional, Set, List
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    combat_helicopter = "combat_helicopter"


class Role(str, Enum):
    user = "user"
    admin = "admin"
    manager = "manager"


class UserDTO(BaseModel):
    id: UUID = uuid4()
    first_name: str
    last_name: Optional[str] = None
    gender: Gender
    roles: List[Role]
    in_charge: Set[UUID] = set()
    managed_by: Optional[UUID] = None
    password: str


class UserResponse(BaseModel):
    id: UUID = uuid4()
    first_name: str
    last_name: Optional[str] = None
    gender: Gender
    roles: List[Role]
    in_charge: Set[UUID] = set()
    managed_by: Optional[UUID] = None


class User(BaseModel):
    id: UUID = uuid4()
    first_name: str
    last_name: Optional[str] = None
    gender: Gender
    roles: List[Role]
    is_activated: bool = True
    activated_at: int = time_ns()  # timestamp
    updated_at: Optional[int] = None  # timestamp
    in_charge: Set[UUID] = set()
    managed_by: Optional[UUID] = None
    entity_type: str = "User"

    @model_validator(mode='after')
    def __manager_validator(self) -> 'User':
        if self.in_charge:
            if not self.is_activated:
                raise ValueError(f'User {self.first_name} is not activated')
            if Role.manager not in self.roles:
                raise ValueError(f'User {self.first_name} is not manager')
        else:
            self.in_charge = set()
        return self

    @field_validator('in_charge', mode='before')
    @classmethod
    def __in_charge_validator(cls, _in_charge: Set[UUID]) -> Set[UUID]:
        if not _in_charge:
            _in_charge = set()
        return _in_charge

    @field_validator('id', mode='before')
    @classmethod
    def __id_validator(cls, _id: UUID) -> UUID:
        if not _id:
            _id = uuid4()
        return _id


class UserDB(User):
    hashed_password: str
