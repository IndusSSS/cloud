from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLITE_URL = "sqlite:///./logs.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id        = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    switch    = Column(Boolean)
    ts_device = Column(Integer)
