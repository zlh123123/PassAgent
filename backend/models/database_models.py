"""
PassAgent Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func

from app.database.database import Base


class PasswordAnalysis(Base):
    """Password analysis results table"""
    __tablename__ = "password_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(64), index=True)  # SHA-256 hash for privacy
    strength_score = Column(Float, nullable=False)
    strength_level = Column(String(20), nullable=False)  # weak, medium, strong, very_strong
    analysis_type = Column(String(50), nullable=False)  # strength, leak, compliance
    analysis_data = Column(JSON)  # Store detailed analysis results
    is_leaked = Column(Boolean, default=False)
    leak_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PasswordRecommendation(Base):
    """Password recommendation results table"""
    __tablename__ = "password_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    recommendation_type = Column(String(50), nullable=False)  # text, image, location
    input_data = Column(JSON)  # Store input parameters
    recommended_passwords = Column(JSON)  # List of recommended passwords
    selected_password = Column(String(255), nullable=True)
    feedback_score = Column(Integer, nullable=True)  # User feedback 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TransformationRule(Base):
    """Hashcat transformation rules table"""
    __tablename__ = "transformation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    original_password_hash = Column(String(64), index=True)
    target_password_hash = Column(String(64), index=True)
    hashcat_rule = Column(String(500), nullable=False)
    rule_description = Column(Text)
    success_rate = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserSession(Base):
    """User session management table"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    user_id = Column(String(255), nullable=True)  # Optional user identification
    session_data = Column(JSON)  # Store session context
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)


class AnalysisLog(Base):
    """Analysis operation logs table"""
    __tablename__ = "analysis_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    operation_type = Column(String(100), nullable=False)
    operation_data = Column(JSON)
    status = Column(String(20), nullable=False)  # success, failed, pending
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FileUpload(Base):
    """File upload tracking table"""
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)  # image, audio
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ComplianceRule(Base):
    """Password compliance rules table"""
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    rule_description = Column(Text)
    rule_config = Column(JSON, nullable=False)  # Rule configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AIModelUsage(Base):
    """AI model usage tracking table"""
    __tablename__ = "ai_model_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    operation_type = Column(String(50), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    response_time = Column(Float, nullable=True)
    session_id = Column(String(255), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
