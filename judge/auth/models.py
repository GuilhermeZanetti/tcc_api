from judge.contrib.models.base import BaseModelMixin
from pydantic import Field
from enum import Enum


class UserType(str, Enum):
    JUDGE = "judge"
    PARTICIPANT = "participant"
    GHOST = "ghost"
    MASTER = "master"


class UserModel(BaseModelMixin):
    username: str = Field(title="Username")
    password_hash: str = Field(title="Password Hash")
    user_type: UserType = Field(title="User Type")
