from sqlalchemy import UUID, Column, ForeignKey, LargeBinary
from app.models.secretContent import SecretContent


class SecretTextContent(SecretContent):
    __tablename__ = "secret_text_content"

    uuid = Column(
        UUID(as_uuid=True), ForeignKey("secret_content.uuid"), primary_key=True
    )
    content = Column(LargeBinary, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "text"}
