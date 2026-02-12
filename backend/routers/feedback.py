"""反馈路由"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User, Message, Feedback
from utils.deps import get_current_user
from schemas.session import FeedbackRequest

router = APIRouter(prefix="/api/messages", tags=["feedback"])


@router.post("/{message_id}/feedback")
def toggle_feedback(
    message_id: str,
    body: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    msg = db.query(Message).filter(Message.message_id == message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    existing = (
        db.query(Feedback)
        .filter(Feedback.message_id == message_id, Feedback.user_id == user.user_id)
        .first()
    )

    if existing:
        if existing.feedback_type == body.feedback_type:
            # Same type -> toggle off (delete)
            db.delete(existing)
            db.commit()
            return {"message": "反馈已取消"}
        else:
            # Different type -> update
            existing.feedback_type = body.feedback_type
            db.commit()
            return {"message": "反馈已记录"}
    else:
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            message_id=message_id,
            user_id=user.user_id,
            feedback_type=body.feedback_type,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        db.add(feedback)
        db.commit()
        return {"message": "反馈已记录"}
