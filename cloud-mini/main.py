from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Base, engine, SessionLocal, Log

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class LogIn(BaseModel):
    device_id: str
    switch: bool
    ts: int

@app.post("/api/v1/logs", status_code=201)
def ingest(log: LogIn, db: Session = Depends(get_db)):
    row = Log(device_id=log.device_id, switch=log.switch, ts_device=log.ts)
    db.add(row); db.commit()
    return {"saved": row.id}
