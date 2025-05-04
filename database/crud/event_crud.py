from database.crud.base.factory import BaseCrudFactory
from database.models.models import Event
from database.schemas.system_schemas import EventCreate, EventUpdate, EventGet


class EventCrud(
    BaseCrudFactory(
        model=Event,
        create_schema=EventCreate,
        update_schema=EventUpdate,
        get_schema=EventGet
    )
):
    pass
