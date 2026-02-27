from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select
from database import get_session
from models import UserSchedule

router = APIRouter(prefix="/schedules")

@router.post("/add")
def add_schedule(
    user_id: int = Form(...), check_time: str = Form(...), 
    frequency: str = Form(...), session: Session = Depends(get_session)
):
    existing_sched = session.exec(
        select(UserSchedule).where(
            UserSchedule.user_id == user_id,
            UserSchedule.check_time == check_time,
            UserSchedule.frequency == frequency
        )
    ).first()

    if existing_sched:
        # 💡 發現重複，回傳 400 錯誤與訊息
        return JSONResponse(status_code=400, content={"message": f"⚠️ {check_time} 的排程已經存在囉！"})

    new_sched = UserSchedule(user_id=user_id, check_time=check_time, frequency=frequency)
    session.add(new_sched)
    session.commit()
    
    # 💡 成功，回傳 200
    return JSONResponse(status_code=200, content={"message": "排程新增成功！"})

@router.post("/delete/{sched_id}")
def delete_schedule(sched_id: int, session: Session = Depends(get_session)):
    item = session.get(UserSchedule, sched_id)
    if item:
        session.delete(item)
        session.commit()
    return RedirectResponse(url="/", status_code=303)