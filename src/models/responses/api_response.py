from src.models.users.user import *
from typing import Any


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Any = {}
