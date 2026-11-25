from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modules.users.schemas import validate_password_strength


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=20, description="Code TOTP ou code de secours")


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str

    _strength = field_validator("password")(validate_password_strength)


class MfaCodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=20)


class MfaDisableRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=6, max_length=20)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=2048)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str

    _strength = field_validator("new_password")(validate_password_strength)


class GoogleIdTokenRequest(BaseModel):
    id_token: str = Field(min_length=20, max_length=4096)
    nonce: str | None = Field(default=None, max_length=128)


class GoogleCodeRequest(BaseModel):
    code: str = Field(min_length=5, max_length=2048)
    redirect_uri: str = Field(min_length=8, max_length=500)
    code_verifier: str = Field(min_length=43, max_length=128)
    nonce: str | None = Field(default=None, max_length=128)


class AuthorizeUrlResponse(BaseModel):
    authorization_url: str
