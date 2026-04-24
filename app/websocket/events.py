from enum import Enum

class EventType(str, Enum):
    USER_CREATED = "USER_CREATED"
    USER_DELETED = "USER_DELETED"
    INVITE_SENT = "INVITE_SENT"
    INVITE_ACCEPTED = "INVITE_ACCEPTED"
    SUBSCRIPTION_UPDATED = "SUBSCRIPTION_UPDATED"
    AI_RESPONSE_READY = "AI_RESPONSE_READY"
    NOTIFICATION = "NOTIFICATION"

def create_event(event_type: EventType, data: dict, org_id: int) -> dict:
    return {
        "type": event_type,
        "data": data,
        "org_id": org_id
    }