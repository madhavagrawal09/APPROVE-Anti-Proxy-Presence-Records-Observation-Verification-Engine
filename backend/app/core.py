from functools import lru_cache
import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "APPROVE API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./approve.db"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: str | None = None
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def allowed_origins(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def settings(): return Settings()

passwords = PasswordHash.recommended()
def hash_password(value: str) -> str: return passwords.hash(value)
def verify_password(value: str, encoded: str) -> bool: return passwords.verify(value, encoded)
def new_refresh_token() -> str: return secrets.token_urlsafe(48)
def hash_token(value: str) -> str: return hashlib.sha256(value.encode()).hexdigest()
def access_token(user_id: int, roles: list[str], must_change: bool) -> str:
    cfg=settings(); now=datetime.now(timezone.utc)
    return jwt.encode({"sub":str(user_id),"roles":roles,"must_change_password":must_change,
      "iat":now,"exp":now+timedelta(minutes=cfg.access_token_minutes),"type":"access"},
      cfg.jwt_secret_key,algorithm=cfg.jwt_algorithm)
def decode_access(value: str):
    cfg=settings(); data=jwt.decode(value,cfg.jwt_secret_key,algorithms=[cfg.jwt_algorithm])
    if data.get("type")!="access" or not data.get("sub"): raise jwt.InvalidTokenError()
    return data
