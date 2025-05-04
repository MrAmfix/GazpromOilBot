from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, UUID4
from database.utils.DefaultEnum import UserRole


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: str
    role: Optional[UserRole] = UserRole.USER
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    speciality: Optional[str] = None
    cur_event_id: Optional[UUID4] = None
    cur_stage_id: Optional[UUID4] = None


class UserUpdate(UserCreate):
    id: UUID4


class UserGet(UserUpdate):
    created_at: datetime


class EventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    named_id: str
    name: str
    start_message: str
    end_message: str
    start_sticker: Optional[str] = None
    end_sticker: Optional[str] = None


class EventUpdate(EventCreate):
    id: UUID4


class EventGet(EventUpdate):
    created_at: datetime


class StageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_number: int
    start_message: str
    end_message: str
    expected_answer: Optional[str] = None
    answer_options: Optional[str] = None
    start_attach: Optional[str] = None
    end_attach: Optional[str] = None
    end_sticker: Optional[str] = None
    event_id: UUID4


class StageUpdate(StageCreate):
    id: UUID4


class StageGet(StageUpdate):
    created_at: datetime


class UserStageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID4
    stage_id: UUID4


class UserStageUpdate(UserStageCreate):
    id: UUID4
    answer_text: Optional[str] = None
    ended_at: Optional[datetime] = None


class UserStageGet(UserStageUpdate):
    started_at: datetime


class NewsletterCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str


class NewsletterUpdate(NewsletterCreate):
    id: UUID4


class NewsletterGet(NewsletterUpdate):
    created_at: datetime


class NewsletterLogCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: str
    status: bool = False
    newsletter_id: UUID4


class NewsletterLogUpdate(NewsletterLogCreate):
    id: UUID4


class NewsletterLogGet(NewsletterLogUpdate):
    created_at: datetime

