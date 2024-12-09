import uuid
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, func
from database import Base
from sqlalchemy.orm import relationship


class Secret(Base):
    __tablename__ = "secret"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creation = Column(DateTime, index=True, nullable=False)
    destruction = Column(DateTime, index=True, nullable=True)
    usage_count = Column(Integer, index=True, nullable=False, default=0)
    usage_limit = Column(Integer, index=True, nullable=True)
    hashed_password = Column(String, index=True, nullable=False)

    content_id = Column(UUID(as_uuid=True), ForeignKey('secret_content.uuid'), nullable=True)

    content = relationship("SecretContent", uselist=False, back_populates="secret")
    logs = relationship("SecretLogs", back_populates="secret")
