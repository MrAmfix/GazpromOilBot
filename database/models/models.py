import uuid
from typing import List, Optional
from sqlalchemy import DateTime, Boolean, Text, ForeignKey, Enum, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from database.utils.DefaultEnum import UserRole
from database.utils.moscow_datetime import datetime_now_moscow


class Base(AsyncAttrs, DeclarativeBase):
    __mapper_args__ = {'eager_defaults': True}


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint(
            "(phone IS NULL OR phone ~ '^((\\+7|7|8)[0-9]{10})$')",
            name='valid_phone'
        ),
        CheckConstraint(
            "(email IS NULL OR email ~ '^[-a-zA-Z0-9_.]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,4}$')",
            name='valid_email'
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"), nullable=False, default=UserRole.USER)
    full_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)
    speciality: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cur_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('events.id'), nullable=True
    )
    cur_event: Mapped[Optional["Event"]] = relationship(
        'Event', back_populates='users', lazy='selectin'
    )
    cur_stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('stages.id'), nullable=True
    )
    cur_stage: Mapped[Optional["Stage"]] = relationship(
        'Stage', back_populates='users', lazy='selectin'
    )

    user_stages: Mapped[List["UserStage"]] = relationship(
        'UserStage', back_populates='user', lazy='selectin'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class Event(Base):
    __tablename__ = 'events'
    __table_args__ = (
        CheckConstraint(
            "char_length(named_id) <= 32 AND named_id ~ '^[a-zA-Z0-9-]+$'",
            name='valid_named_id'
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    named_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    start_message: Mapped[str] = mapped_column(Text, nullable=False)
    end_message: Mapped[str] = mapped_column(Text, nullable=False)
    start_sticker: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_sticker: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[List["User"]] = relationship(
        'User', back_populates='cur_event', lazy='selectin'
    )
    stages: Mapped[List["Stage"]] = relationship(
        'Stage', back_populates='event', lazy='selectin'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class Stage(Base):
    __tablename__ = 'stages'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_message: Mapped[str] = mapped_column(Text, nullable=False)
    mid_message: Mapped[str] = mapped_column(Text, nullable=False)
    end_message: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str] = mapped_column(Text, nullable=True)
    answer_options: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_attach: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_attach: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_sticker: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('events.id'), nullable=False
    )
    event: Mapped["Event"] = relationship(
        'Event', back_populates='stages', lazy='selectin'
    )

    user_stages: Mapped[List["UserStage"]] = relationship(
        'UserStage', back_populates='stage', lazy='selectin'
    )
    users: Mapped[List["User"]] = relationship(
        'User', back_populates='cur_stage', lazy='selectin'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class UserStage(Base):
    __tablename__ = 'user_stages'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False
    )
    user: Mapped["User"] = relationship(
        'User', back_populates='user_stages', lazy='selectin'
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('stages.id'), nullable=False
    )
    stage: Mapped["Stage"] = relationship(
        'Stage', back_populates='user_stages', lazy='selectin'
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)
    ended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)


class Newsletter(Base):
    __tablename__ = 'newsletters'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    newsletter_logs: Mapped[List["NewsletterLog"]] = relationship(
        'NewsletterLog', back_populates='newsletter', lazy='selectin'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class NewsletterLog(Base):
    __tablename__ = 'newsletter_logs'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    newsletter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('newsletters.id'), nullable=False
    )
    newsletter: Mapped["Newsletter"] = relationship(
        'Newsletter', back_populates='newsletter_logs', lazy='selectin'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class Onboarding(Base):
    __tablename__ = 'onboardings'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    start_message_unauthorized: Mapped[str] = mapped_column(Text, nullable=False)
    start_message_authorized: Mapped[str] = mapped_column(Text, nullable=False)

    phone_request: Mapped[str] = mapped_column(Text, nullable=False)
    invalid_phone: Mapped[str] = mapped_column(Text, nullable=False)

    fullname_request: Mapped[str] = mapped_column(Text, nullable=False)
    invalid_fullname: Mapped[str] = mapped_column(Text, nullable=False)

    email_request: Mapped[str] = mapped_column(Text, nullable=False)
    invalid_email: Mapped[str] = mapped_column(Text, nullable=False)

    speciality_request: Mapped[str] = mapped_column(Text, nullable=False)
    invalid_speciality: Mapped[str] = mapped_column(Text, nullable=False)

    success_registration: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)
