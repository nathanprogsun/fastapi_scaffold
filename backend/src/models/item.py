from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.config import settings
from src.db.base_class import Base

if TYPE_CHECKING:
    from .user import User


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(settings.STRING_LEN_LIMIT), index=True)
    description = Column(String(settings.STRING_LEN_LIMIT), index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="items")
