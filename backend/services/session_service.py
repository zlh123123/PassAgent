"""会话 CRUD、标题自动生成"""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession

from database.models import Session, Message


def create_session(db: DBSession, user_id: str) -> dict:
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    session = Session(
        session_id=session_id,
        user_id=user_id,
        title="新对话",
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.session_id,
        "title": session.title,
        "created_at": session.created_at,
    }


def list_sessions(db: DBSession, user_id: str, search: str | None = None) -> list[dict]:
    q = db.query(Session).filter(Session.user_id == user_id)
    if search:
        q = q.filter(Session.title.contains(search))
    sessions = q.order_by(Session.updated_at.desc()).all()
    return [
        {
            "session_id": s.session_id,
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sessions
    ]


def delete_session(db: DBSession, user_id: str, session_id: str) -> bool:
    session = (
        db.query(Session)
        .filter(Session.session_id == session_id, Session.user_id == user_id)
        .first()
    )
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


def get_messages(db: DBSession, user_id: str, session_id: str) -> list[dict]:
    # Verify session belongs to user
    session = (
        db.query(Session)
        .filter(Session.session_id == session_id, Session.user_id == user_id)
        .first()
    )
    if not session:
        return []

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    result = []
    for m in messages:
        feedback = None
        if m.feedback:
            feedback = {"feedback_type": m.feedback.feedback_type}
        agent_steps = None
        if m.agent_steps:
            try:
                agent_steps = json.loads(m.agent_steps)
            except json.JSONDecodeError:
                pass
        result.append({
            "message_id": m.message_id,
            "content": m.content,
            "message_type": m.message_type,
            "created_at": m.created_at,
            "feedback": feedback,
            "agent_steps": agent_steps,
        })
    return result


def save_message(
    db: DBSession,
    session_id: str,
    user_id: str,
    content: str,
    message_type: str,
    agent_steps: list | None = None,
) -> str:
    message_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    msg = Message(
        message_id=message_id,
        session_id=session_id,
        user_id=user_id,
        content=content,
        message_type=message_type,
        agent_steps=json.dumps(agent_steps) if agent_steps else None,
        created_at=now,
    )
    db.add(msg)

    # Update session title from first user message
    if message_type == "human":
        session = db.query(Session).filter(Session.session_id == session_id).first()
        if session:
            session.updated_at = now
            # Auto-generate title from first message
            msg_count = db.query(Message).filter(
                Message.session_id == session_id,
                Message.message_type == "human",
            ).count()
            if msg_count == 0:  # This is the first human message
                session.title = content[:30] + ("..." if len(content) > 30 else "")

    db.commit()
    return message_id
