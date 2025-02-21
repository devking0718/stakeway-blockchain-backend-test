from pydantic import BaseModel, Field, field_validator
import re
from typing import List, Optional

def validate_eth_address(address: str) -> str:
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        raise ValueError('Invalid Ethereum address format')
    return address

class ValidatorRequestCreate(BaseModel):
    num_validators: int = Field(..., gt=0)
    fee_recipient: str
    
    @field_validator('fee_recipient')
    @classmethod  # required for field_validator
    def validate_fee_recipient(cls, v):
        return validate_eth_address(v)

class ValidatorRequestResponse(BaseModel):
    request_id: str
    message: str

class ValidatorStatusResponse(BaseModel):
    status: str
    keys: Optional[List[str]] = None
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    database: str 