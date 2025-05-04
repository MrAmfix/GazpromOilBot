from database.crud.base.factory import BaseCrudFactory
from database.models.models import NewsletterLog
from database.schemas.system_schemas import NewsletterLogCreate, NewsletterLogUpdate, NewsletterLogGet


class NewsletterLogCrud(
    BaseCrudFactory(
        model=NewsletterLog,
        create_schema=NewsletterLogCreate,
        update_schema=NewsletterLogUpdate,
        get_schema=NewsletterLogGet
    )
):
    pass
