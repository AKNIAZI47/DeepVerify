from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from db import users
from security import hash_password, verify_password
from security.jwt_manager import JWTManager, TokenType
from security.password_hasher import PasswordHasher
from datetime import datetime, timedelta
from app_logging import get_security_logger
from dependencies import get_app_settings, get_client_ip
from config.settings import Settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Get security logger
security_logger = get_security_logger()

class Signup(BaseModel):
    name: str
    email: EmailStr
    password: str
    language_pref: str | None = None

class Login(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

async def check_account_lockout(user: dict, settings: Settings) -> tuple[bool, str]:
    """
    Check if account is locked due to failed login attempts.
    
    Args:
        user: User document from database
        settings: Application settings
        
    Returns:
        Tuple of (is_locked, message)
    """
    locked_until = user.get("locked_until")
    
    if locked_until:
        # Check if lockout period has expired
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until)
        
        if datetime.utcnow() < locked_until:
            remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60)
            return True, f"Account is locked. Try again in {remaining_minutes} minutes."
        else:
            # Lockout expired, reset failed attempts
            await users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "failed_login_attempts": 0,
                        "locked_until": None,
                        "last_failed_attempt": None,
                    }
                }
            )
            return False, ""
    
    return False, ""

async def record_failed_login(user: dict, settings: Settings):
    """
    Record a failed login attempt and lock account if threshold exceeded.
    
    Args:
        user: User document from database
        settings: Application settings
    """
    failed_attempts = user.get("failed_login_attempts", 0)
    last_failed = user.get("last_failed_attempt")
    now = datetime.utcnow()
    
    # Check if last failed attempt was within the window
    if last_failed:
        if isinstance(last_failed, str):
            last_failed = datetime.fromisoformat(last_failed)
        
        # Reset counter if outside the window
        if now - last_failed > timedelta(minutes=settings.failed_attempt_window_minutes):
            failed_attempts = 0
    
    failed_attempts += 1
    
    update_data = {
        "failed_login_attempts": failed_attempts,
        "last_failed_attempt": now.isoformat(),
    }
    
    # Lock account if threshold exceeded
    if failed_attempts >= settings.max_failed_login_attempts:
        locked_until = now + timedelta(minutes=settings.account_lockout_minutes)
        update_data["locked_until"] = locked_until.isoformat()
    
    await users.update_one(
        {"_id": user["_id"]},
        {"$set": update_data}
    )

async def reset_failed_attempts(user: dict):
    """
    Reset failed login attempts after successful login.
    
    Args:
        user: User document from database
    """
    await users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "failed_login_attempts": 0,
                "last_failed_attempt": None,
                "locked_until": None,
                "last_login": datetime.utcnow().isoformat(),
            }
        }
    )

@router.post("/signup", response_model=TokenOut)
async def signup(payload: Signup, settings: Settings = Depends(get_app_settings)):
    existing = await users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate password strength
    is_valid, errors = PasswordHasher.validate_password_strength(payload.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"message": "Password does not meet requirements", "errors": errors})
    
    hashed = hash_password(payload.password)
    doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hashed,
        "language_pref": payload.language_pref or "en",
        "failed_login_attempts": 0,
        "locked_until": None,
        "last_failed_attempt": None,
        "last_login": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    res = await users.insert_one(doc)
    uid = str(res.inserted_id)
    
    # Create JWT manager and generate tokens
    jwt_manager = JWTManager(
        secret_key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_minutes=settings.refresh_token_expire_minutes,
    )
    
    return TokenOut(
        access_token=jwt_manager.create_access_token(uid),
        refresh_token=jwt_manager.create_refresh_token(uid),
    )

@router.post("/login", response_model=TokenOut)
async def login(
    payload: Login,
    settings: Settings = Depends(get_app_settings),
    ip_address: str = Depends(get_client_ip)
):
    user = await users.find_one({"email": payload.email})
    
    if not user:
        # Log failed login attempt (don't reveal whether email exists)
        security_logger.log_failed_login(
            email=payload.email,
            ip_address=ip_address,
            reason="invalid_credentials",
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if account is locked
    is_locked, lock_message = await check_account_lockout(user, settings)
    if is_locked:
        security_logger.log_suspicious_activity(
            activity_type="locked_account_access_attempt",
            description="Attempt to access locked account",
            ip_address=ip_address,
            user_id=str(user["_id"]),
        )
        raise HTTPException(status_code=403, detail=lock_message)
    
    # Verify password
    if not verify_password(payload.password, user["password_hash"]):
        # Record failed attempt
        await record_failed_login(user, settings)
        
        # Check if this attempt caused a lockout
        failed_attempts = user.get("failed_login_attempts", 0) + 1
        
        # Log failed login
        security_logger.log_failed_login(
            email=payload.email,
            ip_address=ip_address,
            reason="invalid_password",
            attempts=failed_attempts,
        )
        
        if failed_attempts >= settings.max_failed_login_attempts:
            # Log account lockout
            security_logger.log_account_lockout(
                email=payload.email,
                ip_address=ip_address,
                lockout_duration_minutes=settings.account_lockout_minutes,
            )
            raise HTTPException(
                status_code=403,
                detail=f"Account locked due to too many failed login attempts. Try again in {settings.account_lockout_minutes} minutes."
            )
        
        remaining_attempts = settings.max_failed_login_attempts - failed_attempts
        raise HTTPException(
            status_code=401,
            detail=f"Invalid credentials. {remaining_attempts} attempts remaining before account lockout."
        )
    
    # Successful login - reset failed attempts
    await reset_failed_attempts(user)
    
    uid = str(user["_id"])
    
    # Create JWT manager and generate tokens
    jwt_manager = JWTManager(
        secret_key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_minutes=settings.refresh_token_expire_minutes,
    )
    
    return TokenOut(
        access_token=jwt_manager.create_access_token(uid),
        refresh_token=jwt_manager.create_refresh_token(uid),
    )

class RefreshIn(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=TokenOut)
async def refresh(payload: RefreshIn, settings: Settings = Depends(get_app_settings)):
    try:
        # Create JWT manager
        jwt_manager = JWTManager(
            secret_key=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.access_token_expire_minutes,
            refresh_token_expire_minutes=settings.refresh_token_expire_minutes,
        )
        
        # Verify refresh token and get user ID
        token_data = jwt_manager.verify_token(payload.refresh_token, TokenType.REFRESH)
        uid = token_data["sub"]
        
        return TokenOut(
            access_token=jwt_manager.create_access_token(uid),
            refresh_token=jwt_manager.create_refresh_token(uid),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")