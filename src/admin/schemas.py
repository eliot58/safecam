from pydantic import BaseModel
from src.auth.models import Status

class PydanticChangeStatus(BaseModel):
    old_status: Status
    new_status: Status
    cause: str
    user_id: int