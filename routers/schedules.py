from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models import UserSchedule

router = APIRouter(prefix="/schedules")

@router.post("/add")
def add_schedule(
    user_id: int = Form(...), check_time: str = Form(...), 
    frequency: str = Form(...), session: Session = Depends(get_session)
):
    # 1. CHECK FOR DUPLICATES (The Fix)
    existing_sched = session.exec(
        select(UserSchedule).where(
            UserSchedule.user_id == user_id,
            UserSchedule.check_time == check_time,
            UserSchedule.frequency == frequency
        )
    ).first()

    # 2. Add New Schedule ONLY if it doesn't exist
    if not existing_sched:
        new_sched = UserSchedule(user_id=user_id, check_time=check_time, frequency=frequency)
        session.add(new_sched)
        session.commit()
        
    return RedirectResponse(url="/", status_code=303)

@router.post("/delete/{sched_id}")
def delete_schedule(sched_id: int, session: Session = Depends(get_session)):
    item = session.get(UserSchedule, sched_id)
    if item:
        session.delete(item)
        session.commit()
    return RedirectResponse(url="/", status_code=303)