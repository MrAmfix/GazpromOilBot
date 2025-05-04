from database.crud.base.factory import BaseCrudFactory
from database.models.models import Newsletter
from database.schemas.system_schemas import NewsletterCreate, NewsletterUpdate, NewsletterGet


class NewsletterCrud(
    BaseCrudFactory(
        model=Newsletter,
        create_schema=NewsletterCreate,
        update_schema=NewsletterUpdate,
        get_schema=NewsletterGet
    )
):
    pass
