from sqlalchemy import Column, String, Integer, Enum as SQLEnum, DateTime
from sqlalchemy.orm import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class RequestStatus(str, enum.Enum):
    STARTED = "started"
    SUCCESSFUL = "successful"
    FAILED = "failed"

class ValidatorRequest(Base):
    __tablename__ = "validator_requests"
    
    request_id = Column(String, primary_key=True)
    num_validators = Column(Integer, nullable=False)
    fee_recipient = Column(String, nullable=False)
    status = Column(SQLEnum(RequestStatus), nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ValidatorKey(Base):
    __tablename__ = "validator_keys"
    
    key = Column(String, primary_key=True)
    request_id = Column(String, nullable=False)
    fee_recipient = Column(String, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False) 