from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

pg_password = os.environ.get('POSTGRES_PASSWORD')
pg_user = os.environ.get('POSTGRES_USER')
pg_ip = os.environ.get('POSTGRES_IP')
pg_name = os.environ.get('POSTGRES_DB')

SQLALCHEMY_DATABASE_URL = f"""postgresql://{pg_user}:{pg_password}@{pg_ip}/{pg_name}"""

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    import models
    Base.metadata.create_all(bind=engine)
