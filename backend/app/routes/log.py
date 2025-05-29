from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Log
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["logs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LogIn(BaseModel):
    device_id: str
    switch: bool
    ts: int

@router.post("/logs", status_code=201)
def ingest(log: LogIn, db: Session = Depends(get_db)):
    row = Log(device_id=log.device_id, switch=log.switch, ts_device=log.ts)
    db.add(row)
    db.commit()
    return {"ok": True}
