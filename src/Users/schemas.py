from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class GenderEnum(str, Enum):
    Мужчина = "Мужчина"
    Женщина = "Женщина"


class ParticipantBase(BaseModel):
    gender: GenderEnum = Field(..., description="Пол участника")
    first_name: str = Field(..., description="Имя участника")
    last_name: str = Field(..., description="Фамилия участника")
    email: EmailStr = Field(..., description="Электронная почта участника")


class ParticipantCreate(ParticipantBase):
    password: str = Field(..., description="Пароль для авторизации")


class ParticipantResponse(ParticipantBase):
    id: int = Field(..., description="Идентификатор участника")
    is_active: bool = Field(..., description="Активен ли участник")
    avatar_url: Optional[str] = Field(None, description="Ссылка на аватар участника")
    created_at: datetime = Field(..., description="Дата регистрации участника")

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_avatar(cls, participant, avatar_url: Optional[str] = None):
        return cls(
            id=participant.id,
            gender=participant.gender,
            first_name=participant.first_name,
            last_name=participant.last_name,
            email=participant.email,
            is_active=participant.is_active,
            avatar_url=avatar_url,
            created_at=participant.created_at,
        )


class MatchRequest(BaseModel):
    user_id: int = Field(
        ..., description="Идентификатор пользователя, который ставит лайк"
    )


class MatchResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате лайка")
    email: Optional[EmailStr] = Field(
        None, description="Электронная почта участника при взаимной симпатии"
    )
