from pydantic import BaseModel, EmailStr
from typing import Optional
import base64


class ParticipantBase(BaseModel):
    gender: str
    first_name: str
    last_name: str
    email: EmailStr


class ParticipantCreate(ParticipantBase):
    password: str


class ParticipantResponse(ParticipantBase):
    id: int
    is_active: bool
    avatar: Optional[str] = None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm_with_avatar(cls, participant):
        """Создание экземпляра с кодированием аватара в Base64."""
        avatar_base64 = (
            base64.b64encode(participant.avatar).decode("utf-8")
            if participant.avatar
            else None
        )
        return cls(
            id=participant.id,
            gender=participant.gender,
            first_name=participant.first_name,
            last_name=participant.last_name,
            email=participant.email,
            is_active=participant.is_active,
            avatar=avatar_base64,
        )
