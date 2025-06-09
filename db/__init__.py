from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_PATH

engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
