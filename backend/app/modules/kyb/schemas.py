from pydantic import BaseModel


class KYBCheckRequest(BaseModel):
    organization_name: str
