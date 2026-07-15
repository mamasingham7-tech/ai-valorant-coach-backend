from enum import Enum

class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    COACH = "coach"
    ADMIN = "admin"
