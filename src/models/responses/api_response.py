from models.users.user import *
from typing import Union


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Union[UserResponse, List[UserResponse]] = {}
