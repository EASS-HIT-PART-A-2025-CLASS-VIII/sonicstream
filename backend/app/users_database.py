from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from .models.users import Base

# Users database path (separate from tracks)
USERS_DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.sqlite")
USERS_DATABASE_URL = f"sqlite:///{USERS_DATABASE_PATH}"

users_engine = create_engine(USERS_DATABASE_URL, connect_args={"check_same_thread": False})
UsersSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=users_engine)


def init_users_db():
    """Create the users database tables."""
    Base.metadata.create_all(bind=users_engine)


def get_users_db():
    """Dependency for getting users database session."""
    db = UsersSessionLocal()
    try:
        yield db
    finally:
        db.close()
