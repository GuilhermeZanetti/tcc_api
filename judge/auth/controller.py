from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from judge.auth.schemas import UserIn, UserOut, TokenResponse
from judge.auth.usecases import AuthUseCase
from judge.auth.models import UserType

router = APIRouter(tags=["auth"], prefix="/v0/auth")


@router.post("/register", 
             response_model=UserOut, 
             status_code=status.HTTP_201_CREATED)
async def register(user_in: UserIn, 
                   user_type: UserType, 
                   use_case: AuthUseCase = Depends()
                ) -> UserOut:
    user = await use_case.register_user(user_in=user_in, user_type=user_type)
    return UserOut(**user.model_dump())


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), 
                use_case: AuthUseCase = Depends()
            ) -> TokenResponse:
    user = await use_case.authenticate_user(form_data.username, form_data.password)
    access_token = use_case.create_access_token(data={"sub": user.username, "type": user.user_type})
    return TokenResponse(access_token=access_token)
