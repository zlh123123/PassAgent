"""会话路由：CRUD sessions + messages"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User
from utils.deps import get_current_user
from schemas.session import SessionResponse, SessionsListResponse, MessagesListResponse, RenameSessionRequest
from services.session_service import (
    create_session,
    list_sessions,
    delete_session,
    rename_session,
    get_messages,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def create(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    result = create_session(db, user.user_id)
    return SessionResponse(**result)


@router.get("", response_model=SessionsListResponse)
def list_all(
    search: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    sessions = list_sessions(db, user.user_id, search)
    return SessionsListResponse(sessions=sessions)


@router.put("/{session_id}/title", response_model=SessionResponse)
def rename(
    session_id: str,
    body: RenameSessionRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    result = rename_session(db, user.user_id, session_id, body.title)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return SessionResponse(**result)


@router.delete("")
def delete_all_sessions(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    from database.models import Session as SessionModel
    db.query(SessionModel).filter(SessionModel.user_id == user.user_id).delete()
    db.commit()
    return {"message": "已清除全部会话"}


@router.delete("/{session_id}")
def delete(
    session_id: str,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    ok = delete_session(db, user.user_id, session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return {"message": "已删除"}


@router.get("/{session_id}/messages", response_model=MessagesListResponse)
def messages(
    session_id: str,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    msgs = get_messages(db, user.user_id, session_id)
    return MessagesListResponse(messages=msgs)
