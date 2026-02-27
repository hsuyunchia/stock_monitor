from fastapi import APIRouter, Depends, Form
from sqlmodel import Session, select
from database import get_session
from models import UserSchedule
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/schedules")

@router.post("/add")
def add_schedule(
    user_id: int = Form(...), check_time: str = Form(...), 
    frequency: str = Form(...), session: Session = Depends(get_session)
):
    # 簡單防呆: 檢查時間格式是否正確 (略)
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