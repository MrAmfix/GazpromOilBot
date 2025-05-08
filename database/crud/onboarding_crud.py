import uuid
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud.base.factory import BaseCrudFactory
from database.models.models import Onboarding
from database.schemas.system_schemas import OnboardingCreate, OnboardingUpdate, OnboardingGet
from database.utils.moscow_datetime import datetime_now_moscow


class OnboardingCrud(
    BaseCrudFactory(
        model=Onboarding,
        create_schema=OnboardingCreate,
        update_schema=OnboardingUpdate,
        get_schema=OnboardingGet
    )
):
    @staticmethod
    async def get_last_onboarding(session: AsyncSession) -> OnboardingGet:
        default_onboarding = OnboardingGet(
            id=uuid.uuid4(),
            start_message_unauthorized='Привет, давай для начала зарегистрируемся',
            start_message_authorized='Привет, ты уже зарегистрирован 🤝',
            phone_request='Отправь пожалуйста свой номер телефона',
            invalid_phone='Отправь пожалуйста телефон по кнопке',
            fullname_request='Спасибо, теперь мне необходимо знать твое ФИО',
            invalid_fullname='Пожалуйста, отправь свое ФИО текстом',
            email_request='Спасибо, теперь мне нужна ваша электронная почта',
            invalid_email='Некорректный формат, введите пожалуйста почту в формате email@example.com',
            speciality_request='Спасибо, осталось узнать только вашу специальность, напишите ее',
            invalid_speciality='Пожалуйста, отправь свое специальность текстом',
            success_registration='Спасибо, теперь ты зарегистрирован 🔥',
            created_at=datetime_now_moscow()
        )

        result = await session.execute(
            select(Onboarding)
            .order_by(desc(Onboarding.created_at))
            .limit(1)
        )
        onboarding = result.scalar_one_or_none()
        return OnboardingGet.model_validate(onboarding) if onboarding else default_onboarding
