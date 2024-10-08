import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

class Database:
    def __init__(self):
        load_dotenv()
        self.DATABASE_USER = os.getenv("DATABASE_USER")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.SQLALCHEMY_DATABASE_URL = (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
        self.engine = self.create_engine()
        self.SessionLocal = self.create_session()
        self.Base = self.create_base()

    def create_engine(self):
        """
        Crear un motor de base de datos SQLAlchemy
        """
        return create_engine(self.SQLALCHEMY_DATABASE_URL)

    def create_session(self):
        """
        Crear una sesión de base de datos SQLAlchemy
        """
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_base(self):
        """
        Crear una clase base de SQLAlchemy
        """
        return declarative_base()

# Usage
db = Database()
engine = db.engine
SessionLocal = db.SessionLocal
Base = db.Base