from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True) # Clerk user_id is a string
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    orders_shipped = Column(String, nullable=True)
    role = Column(String, default="member") # 'admin' or 'member'
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    email = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    orders_shipped = Column(String, nullable=True)
    query_text = Column(Text)
    response_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    retrieved_sop = Column(Text, nullable=True)
    response_status = Column(String, nullable=True)
    
    user = relationship("User")

class QueryFeedback(Base):
    __tablename__ = "query_feedback"
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, ForeignKey("chat_logs.id"))
    user_id = Column(String, ForeignKey("users.id"))
    feedback_type = Column(String) # "like" or "dislike"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('query_log_id', 'user_id', name='_user_query_feedback_uc'),)
    
    query_log = relationship("ChatLog")
    user = relationship("User")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), index=True)
    content = Column(Text)
    # Dimension 768 for 'text-embedding-004'
    embedding = Column(Vector(768))
    # Metadata for additional context like document name, page etc.
    metadata_json = Column(Text, nullable=True) 

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    storage_url = Column(String)
    status = Column(String, default="uploaded") # uploaded, processing, ready, failed
    created_at = Column(DateTime, default=datetime.utcnow)
