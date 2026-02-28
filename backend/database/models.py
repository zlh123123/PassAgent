"""数据库设计"""
from sqlalchemy import Column, Text, Integer, LargeBinary, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    user_id = Column(Text, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    nickname = Column(Text)
    theme = Column(Text, default="system")
    font_size = Column(Text, default="M")
    bubble_style = Column(Text, default="rounded")
    gen_auto_mode = Column(Integer, default=1)
    gen_security_weight = Column(Text, default="0.5")
    created_at = Column(Text, server_default="CURRENT_TIMESTAMP")

    # 关系
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"

    session_id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    title = Column(Text, default="新对话")
    created_at = Column(Text, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(Text)

    # 关系
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="session")
    tasks = relationship("Task", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    message_id = Column(Text, primary_key=True)
    session_id = Column(Text, ForeignKey("sessions.session_id"), nullable=False)
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Text, nullable=False)  # human / assistant
    agent_steps = Column(Text)  # JSON 数组
    created_at = Column(Text, server_default="CURRENT_TIMESTAMP")

    # 关系
    session = relationship("Session", back_populates="messages")
    user = relationship("User", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", uselist=False, cascade="all, delete-orphan")


class Feedback(Base):
    """反馈表"""
    __tablename__ = "feedback"

    feedback_id = Column(Text, primary_key=True)
    message_id = Column(Text, ForeignKey("messages.message_id"), unique=True, nullable=False)
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    feedback_type = Column(Text, nullable=False)  # like / dislike
    created_at = Column(Text, server_default="CURRENT_TIMESTAMP")

    # 关系
    message = relationship("Message", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")


class UploadedFile(Base):
    """上传文件表"""
    __tablename__ = "uploaded_files"

    file_id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    session_id = Column(Text, ForeignKey("sessions.session_id"))  # 可为空
    filename = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer)
    file_type = Column(Text)  # MIME 类型
    extracted_text = Column(Text)  # Omni 模型解析后的文本
    uploaded_at = Column(Text, server_default="CURRENT_TIMESTAMP")

    # 关系
    user = relationship("User", back_populates="uploaded_files")
    session = relationship("Session", back_populates="uploaded_files")


class UserMemory(Base):
    """用户记忆表"""
    __tablename__ = "user_memories"

    memory_id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    memory_type = Column(Text, nullable=False)  # PREFERENCE / FACT / CONSTRAINT
    source = Column(Text, default="auto")  # auto / manual
    embedding = Column(LargeBinary)  # 文本向量，用于语义检索
    created_at = Column(Text, server_default="CURRENT_TIMESTAMP")

    # 关系
    user = relationship("User", back_populates="memories")


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"

    task_id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False)
    session_id = Column(Text, ForeignKey("sessions.session_id"), nullable=False)
    message_content = Column(Text, nullable=False)
    file_ids = Column(Text)  # JSON 数组
    status = Column(Text, default="pending")  # pending / processing / success / fail
    error_message = Column(Text)
    created_at = Column(Text, server_default="CURRENT_TIMESTAMP")
    started_at = Column(Text)
    finished_at = Column(Text)

    # 关系
    user = relationship("User", back_populates="tasks")
    session = relationship("Session", back_populates="tasks")
