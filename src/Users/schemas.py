from pydantic import BaseModel, EmailStr


class ParticipantBase(BaseModel):
    avatar: str | None = None
    gender: str
    first_name: str
    last_name: str
    email: EmailStr


class ParticipantCreate(ParticipantBase):
    password: str


class ParticipantResponse(ParticipantBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
