from src.crud.base import CRUDBase
from src.models import Role
from src.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    ...


role = CRUDRole(Role)
