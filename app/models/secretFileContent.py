from sqlalchemy import UUID, Column, ForeignKey, String
from models.secretContent import SecretContent


class SecretFileContent(SecretContent):
    __tablename__ = "secret_file_content"

    uuid = Column(
        UUID(as_uuid=True), ForeignKey("secret_content.uuid"), primary_key=True
    )
    content = Column(String, nullable=False)
    filename = Column(String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "file"}
