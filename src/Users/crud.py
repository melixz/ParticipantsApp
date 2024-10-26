from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Participant
from .schemas import ParticipantCreate
from typing import Optional
from src.utils.logging import AppLogger

logger = AppLogger().get_logger()


class ParticipantCRUD:
    @staticmethod
    async def get_participant_by_email(
        db: AsyncSession, email: str
    ) -> Optional[Participant]:
        """Получение участника по email."""
        result = await db.execute(select(Participant).filter_by(email=email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_participant(
        db: AsyncSession,
        participant_data: ParticipantCreate,
        hashed_password: str,
        avatar: bytes,
    ) -> Optional[Participant | bool]:
        """Создание нового участника с хэшированным паролем и аватаркой."""
        new_participant = Participant(
            avatar=avatar,
            gender=participant_data.gender,
            first_name=participant_data.first_name,
            last_name=participant_data.last_name,
            email=participant_data.email,
            hashed_password=hashed_password,
        )

        try:
            db.add(new_participant)
            await db.commit()
            await db.refresh(new_participant)
            return new_participant
        except Exception as e:
            await db.rollback()
            logger.error("Ошибка при создании участника: %s", e)
            return False
