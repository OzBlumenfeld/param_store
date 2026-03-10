from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Parameter(Base):
    __tablename__ = "parameters"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    app: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_dek: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Encrypted Data Encryption Key
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Parameter(user_id={self.user_id}, app={self.app}, name={self.name})>"
