from enum import Enum


class LampState(Enum):
    SETLIGHT = 1
    IDLE = 2
    IDLENOTCONNECT = 3
    NOTIDLE = 4
