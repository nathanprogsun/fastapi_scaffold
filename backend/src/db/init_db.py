from sqlalchemy.orm import Session

from src.config import settings
from src import crud, schemas
from src.constants import Roles
from src.utils.security import frontend_hash


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    roles = crud.role.get_multi(db)
    if not roles:
        for role in [Roles.NORMAL, Roles.ADMIN, Roles.SUPER_ADMIN]:
            role_in = schemas.RoleCreate(name=role.name, description=role.description)
            crud.role.create(db, obj_in=role_in)

    user = crud.user.get_by_email(db, email=settings.FIRST_ADMIN)
    if not user:
        password = frontend_hash(settings.FIRST_ADMIN_PASSWORD)
        user_in = schemas.UserCreate(
            email=settings.FIRST_ADMIN,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        user = crud.user.activate(db, user=user)
        user = crud.user.update_role(db, user=user, role=schemas.UserRole.SUPER_ADMIN)

    ...
