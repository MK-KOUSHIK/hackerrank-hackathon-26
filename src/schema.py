from enum import Enum
from pydantic import BaseModel, Field, field_validator

class ActionEnum(str, Enum):
    NOTIFY = "notify"
    DIGEST = "digest"
    MUTE = "mute"

class MessageTypeEnum(str, Enum):
    PERSONAL = "personal"
    URGENT = "urgent"
    EVENT = "event"
    PAYMENT = "payment"
    BUSINESS_UPDATE = "business_update"
    PROMOTION = "promotion"
    GREETING = "greeting"
    FORWARD = "forward"
    SPAM = "spam"
    SCAM = "scam"
    UNKNOWN = "unknown"

class PredictionOutputRow(BaseModel):
    message_id: str
    action: ActionEnum
    message_type: MessageTypeEnum
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_message_ids: str = "none"

    @field_validator("confidence")
    def round_confidence(cls, v):
        return round(float(v), 2)
