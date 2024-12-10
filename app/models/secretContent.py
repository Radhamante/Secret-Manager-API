import uuid
from sqlalchemy import UUID, Column, String
from sqlalchemy.orm import relationship
from app.database import Base


class SecretContent(Base):
    __tablename__ = "secret_content"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)
    secret = relationship("Secret", uselist=False, back_populates="content")

    __mapper_args__ = {"polymorphic_identity": "secret_content", "polymorphic_on": type}
