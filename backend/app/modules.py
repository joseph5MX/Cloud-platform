from datetime import datetime, timezone
from sqlalchemy import String, Text, Datetime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="customer")

class Service(Base)
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    container_id: Mapped[str | None] = mapped_column(string, nullable=True)
    status: Mapped[str] = mapped_column(string, default="provisioning")
    storage_location: Mapped[str] = mapped_column(
        String, default="Bostwana (local server)")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(ForeignKey("users.id"))
cat > app/modules.py << 'EOF'
from datetime import datetime, timezone
from sqlalchemy import String, Text, Datetime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="customer")

class Service(Base)
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    container_id: Mapped[str | None] = mapped_column(string, nullable=True)
    status: Mapped[str] = mapped_column(string, default="provisioning")
    storage_location: Mapped[str] = mapped_column(
        String, default="Bostwana (local server)")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(primary_key=True)
  actor_id: Mapped[str] = mapped_column(Foreignkey("users.id"))
  service_id: Mapped[int | None] = mapped_column(
      ForeignKey("services.id"), nullable=True)
  action: Mapped[str] = mapped_column(string)
  resources: Mapped[str] = mapped_column(String)
  timestamp: Mapped[datetime] = mapped_column(
      DateTime(timezone=True), default=now)


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id), nullable=True)
    wazuh_alert_id: Mapped[str | None] = mapped_column(String, nullable=True)
    severity: Mapped[str] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    generated_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    period_month: Mapped[int] = mapped_column()
    period_year: Mapped[int] = mapped_column()
    file_path: Mapped[str] = mapped_column(String)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now)
