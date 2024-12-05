from sqlalchemy import UUID, Column, ForeignKey, String
from models.secretContent import SecretContent


class SecretTextContent(SecretContent):
    __tablename__ = "secret_text_content"

    uuid = Column(
        UUID(as_uuid=True), ForeignKey("secret_content.uuid"), primary_key=True
    )
    content = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "text"}
