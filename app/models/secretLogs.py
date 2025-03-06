import uuid
from sqlalchemy import UUID, Column, Enum, ForeignKey, DateTime, func
from app.database import Base
from sqlalchemy.orm import relationship

from app.schemas.secretLog import SecretLogActionEnum


class SecretLogs(Base):
    __tablename__ = "secretLogs"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(Enum(SecretLogActionEnum), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    secret_id = Column(UUID(as_uuid=True), ForeignKey("secret.uuid"), nullable=False)
    secret = relationship("Secret", back_populates="logs")
