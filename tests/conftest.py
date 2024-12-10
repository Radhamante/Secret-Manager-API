import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base


@pytest.fixture
def db_session():
    # Création d'une base SQLite en mémoire
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Création des tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db

    # Fermeture et suppression
    db.close()
