from pydantic import BaseModel


class LivenessRequest(BaseModel):
    session_id: str
