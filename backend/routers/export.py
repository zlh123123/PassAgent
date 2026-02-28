"""数据导出路由"""
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User, Session as SessionModel, Message, UserMemory
from utils.deps import get_current_user

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/conversations")
def export_conversations(
    session_id: str | None = Query(None),
    format: str = Query("json"),
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    query = db.query(SessionModel).filter(SessionModel.user_id == user.user_id)
    if session_id:
        query = query.filter(SessionModel.session_id == session_id)
    sessions = query.order_by(SessionModel.created_at.desc()).all()

    result = []
    for s in sessions:
        msgs = (
            db.query(Message)
            .filter(Message.session_id == s.session_id)
            .order_by(Message.created_at)
            .all()
        )
        result.append({
            "session_id": s.session_id,
            "title": s.title,
            "created_at": s.created_at,
            "messages": [
                {
                    "message_id": m.message_id,
                    "content": m.content,
                    "message_type": m.message_type,
                    "created_at": m.created_at,
                }
                for m in msgs
            ],
        })
    return {"conversations": result, "format": format}


@router.get("/memories")
def export_memories(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    memories = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user.user_id)
        .order_by(UserMemory.created_at.desc())
        .all()
    )
    return {
        "memories": [
            {
                "memory_id": m.memory_id,
                "content": m.content,
                "memory_type": m.memory_type,
                "source": m.source or "auto",
                "created_at": m.created_at,
            }
            for m in memories
        ]
    }


@router.get("/settings")
def export_settings(
    user: User = Depends(get_current_user),
):
    return {
        "settings": {
            "nickname": user.nickname,
            "theme": user.theme or "system",
            "font_size": user.font_size or "M",
            "bubble_style": user.bubble_style or "rounded",
            "gen_auto_mode": user.gen_auto_mode if user.gen_auto_mode is not None else 1,
            "gen_security_weight": user.gen_security_weight or "0.5",
        }
    }
