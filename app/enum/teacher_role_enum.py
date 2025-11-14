# app/enum/teacher_role_enum.py
from enum import Enum

class TeacherRole(str, Enum):
    PRIMARY = "PRIMARY"
    ASSISTANT = "ASSISTANT"
    GUEST = "GUEST"