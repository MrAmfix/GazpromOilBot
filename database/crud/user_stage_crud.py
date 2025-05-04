from database.crud.base.factory import BaseCrudFactory
from database.models.models import UserStage
from database.schemas.system_schemas import UserStageCreate, UserStageUpdate, UserStageGet


class UserStageCrud(
    BaseCrudFactory(
        model=UserStage,
        create_schema=UserStageCreate,
        update_schema=UserStageUpdate,
        get_schema=UserStageGet
    )
):
    pass
