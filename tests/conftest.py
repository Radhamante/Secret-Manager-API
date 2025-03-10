from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base
from app.hash_manager import hash_password
from app.models.user import User
from uuid import uuid4


@pytest.fixture(scope="session")
def db_session() -> Generator[Session]:
    # Création d'une base SQLite en mémoire
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Création des tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    yield db

    # Fermeture et suppression
    db.close()


@pytest.fixture(scope="session")
def user(db_session: Session) -> User:
    # Ajoute un utilisateur de test
    test_user = User(
        uuid=uuid4(),
        username="testuser",
        hashed_password=hash_password("password"),
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    return test_user
