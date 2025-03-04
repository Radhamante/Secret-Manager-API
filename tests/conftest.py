import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
import uuid

uuid = uuid.UUID("550e8400-e29b-41d4-a716-446655440000", version=4)


@pytest.fixture
def db_session():
    # Création d'une base SQLite en mémoire
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Création des tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Ajoute un utilisateur de test
    test_user = User(
        uuid=uuid,
        username="testuser",
        hashed_password="hashedpassword",
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    yield db

    # Fermeture et suppression
    db.close()


@pytest.fixture
def user():
    return User(
        uuid=uuid,
        username="testuser",
        hashed_password="hashedpassword",
    )
