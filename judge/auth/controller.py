from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from judge.auth.schemas import UserIn, UserOut, TokenResponse
from judge.auth.usecases import AuthUseCase
from judge.auth.models import UserType
from judge.contrib.documentation import ForbiddenErrorResponse, InternalServerErrorResponse, NotFoundErrorResponse, UnprocessableEntityErrorResponse, ValidationErrorResponse
from judge.contrib.exceptions import ValidationError
from judge.config import settings

router = APIRouter(tags=["auth"], prefix="/v0/auth")

def validate_api_key(x_api_key: str = Header(None)):
    """
    Valida a API_KEY_MASTER recebida no cabeçalho HTTP.
    """
    if x_api_key != settings.API_KEY_MASTER.get_secret_value():
        raise HTTPException(status_code=403, detail="Acesso não autorizado")

@router.post("/register", 
             summary="Register a new user",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {'model': UserOut},
                 400: {'model': ValidationErrorResponse},
                 403: {'model': ForbiddenErrorResponse},
                 500: {'model': InternalServerErrorResponse},
             },
             response_model=UserOut,
             )
async def register(user_in: UserIn, 
                   user_type: UserType, 
                   use_case: AuthUseCase = Depends(),
                   x_api_key: str = Depends(validate_api_key)
                ) -> UserOut:
    try:
        
        if user_type not in UserType:
            raise ValidationError(field="user_type", message="Invalid user type")
        
        existing_user = await use_case.repository.get(filter={"username": user_in.username})
        if existing_user:
            raise ValidationError(field="username", message="Username already exists")
        
        if user_in.password == "":
            raise ValidationError(field="password", message="Password cannot be empty")
        if len(user_in.password) < 8:
            raise ValidationError(field="password", message="Password must be at least 8 characters long")
        if not any(char.isdigit() for char in user_in.password):
            raise ValidationError(field="password", message="Password must contain at least one digit")
        if not any(char.isalpha() for char in user_in.password):
            raise ValidationError(field="password", message="Password must contain at least one letter")
        if not any(char in "!@#$%^&*()-_=+[]{};:,.<>?/" for char in user_in.password):
            raise ValidationError(field="password", message="Password must contain at least one special character")
        if user_in.username == user_in.password:
            raise ValidationError(field="password", message="Password cannot be the same as username")
        if user_in.username == user_type:
            raise ValidationError(field="username", message="Username cannot be the same as user type")
        if user_in.password == user_type:
            raise ValidationError(field="password", message="Password cannot be the same as user type")
        
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ve.errors(),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
    user = await use_case.register_user(user_in=user_in, user_type=user_type)
    return UserOut(**user.model_dump())


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful login",
            "model": TokenResponse,  
        },
        404: {'model': NotFoundErrorResponse},
        422: {'model': UnprocessableEntityErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), 
                use_case: AuthUseCase = Depends()
            ) -> TokenResponse:
    user = await use_case.authenticate_user(form_data.username, form_data.password)
    access_token = use_case.create_access_token(data={"sub": user.username, "type": user.user_type})
    return TokenResponse(access_token=access_token)
