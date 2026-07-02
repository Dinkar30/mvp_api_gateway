from app.database import Base
from sqlalchemy.sql import func 
from sqlalchemy import ForeignKey , Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class RequestLog(Base):
    __tablename__ = "requestlogs"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    method: Mapped[str] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(index=True)
    status_code: Mapped[int] = mapped_column(index=True)
    latency: Mapped[float] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="request_logs")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(index=True,primary_key=True)
    username: Mapped[str] = mapped_column( unique=True)
    api: Mapped[list["APIKey"]] = relationship(back_populates="user")
    request_logs: Mapped[list["RequestLog"]] = relationship(back_populates="user")
    rate_limit: Mapped[int] = mapped_column(default=10)
    hashed_password: Mapped[str] = mapped_column()

class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    hashed_key: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped["User"] = relationship(back_populates="api")

class Service(Base):
    __tablename__ = "services"
    
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str] = mapped_column(unique=True)
    prefix: Mapped[str] = mapped_column()
    target_url: Mapped[str] = mapped_column()
    is_healthy: Mapped[bool] = mapped_column(default=True)
    last_checked: Mapped[datetime] = mapped_column(nullable=True)
