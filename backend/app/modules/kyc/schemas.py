from pydantic import BaseModel


class KYCCheckRequest(BaseModel):
    document_type: str
