from fastapi import Depends
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from judge.auth.models import UserModel, UserType
from judge.auth.repositories import UserRepository
from judge.auth.schemas import UserIn, TokenResponse
from judge.config import settings
from judge.contrib.exceptions import ObjectNotFound, ValidationError
from uuid import uuid4  # Add this import


class AuthUseCase:
    def __init__(
        self, 
        repository: UserRepository = Depends(),
    ) -> None:
        self.repository = repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v0/auth/login")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    async def authenticate_user(self, username: str, password: str) -> UserModel:
        user = await self.repository.get(filter={"username": username})
        print("USER FROM DB:", user)
        if not user or not self.verify_password(password, user["password_hash"]):
            raise ValidationError(field="username", message="Invalid credentials")
        return UserModel(**user)

    async def register_user(self, user_in: UserIn, user_type: UserType) -> UserModel:
        hashed_password = self.hash_password(user_in.password)
        print("hash password:", hashed_password)
        print("user_in:", user_in)
        print("user_type:", user_type)
        _id = str(uuid4())
        print("Generated UUID:", _id)
        
        user = UserModel(
            id=_id,
            username=user_in.username,
            password_hash=hashed_password,
            user_type=user_type,
        )
        await self.repository.insert(model=user)
        return user
