from pydantic import BaseModel


class FaceMatchRequest(BaseModel):
    reference_image_id: str
    capture_image_id: str
