from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv('DB_USER', "root")
DB_PASSWORD = os.getenv('DB_PASSWORD', "")
DB_HOST = os.getenv('DB_HOST', "localhost")
DB_PORT = os.getenv('DB_PORT', "3306")
DB_NAME = os.getenv('DB_NAME', "motor_scale_system_db")

DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URL, echo=os.getenv("DB_ECHO", "false") == "true")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()