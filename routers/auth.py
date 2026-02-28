from fastapi import APIRouter, Depends, Form, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models import User
from services.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(
    email: str = Form(...), 
    password: str = Form(...), 
    session: Session = Depends(get_session)
):
    # 1. 檢查信箱是否已被註冊
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        return JSONResponse(status_code=400, content={"message": "這個信箱已經註冊過囉！"})
    
    # 2. 建立新使用者並加密密碼
    new_user = User(
        email=email, 
        hashed_password=get_password_hash(password)
    )
    session.add(new_user)
    session.commit()
    
    return JSONResponse(status_code=200, content={"message": "註冊成功！請切換到登入頁面。"})

@router.post("/login")
def login(
    email: str = Form(...), 
    password: str = Form(...), 
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return JSONResponse(status_code=400, content={"message": "信箱或密碼錯誤。"})
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 💡 建立 Response 物件
    content = {"message": "登入成功！"}
    response = JSONResponse(content=content)
    
    # 💡 使用最原始、最通用的 Cookie 設定，繞過瀏覽器對安全性欄位的挑剔
    response.set_cookie(
        key="access_token", 
        value=access_token,
        path="/",
        httponly=False,  # 💡 暫時設為 False，讓我們在 Application 頁面看得到它
        samesite="lax",
        secure=False
    )
    
    return response

@router.get("/logout")
def logout(response: Response):
    # 💡 建立回應物件
    response = RedirectResponse(url="/login", status_code=303)
    
    # 💡 刪除時必須確保 path 與設定時完全一致
    response.delete_cookie(
        key="access_token",
        path="/",        # 👈 這是關鍵，必須加上這行
        httponly=False,  # 如果你之前改過 False，這裡最好也對應
        samesite="lax"
    )
    return response