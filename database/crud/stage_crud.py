from database.crud.base.factory import BaseCrudFactory
from database.models.models import Stage
from database.schemas.system_schemas import StageCreate, StageUpdate, StageGet


class StageCrud(
    BaseCrudFactory(
        model=Stage,
        create_schema=StageCreate,
        update_schema=StageUpdate,
        get_schema=StageGet
    )
):
    pass
