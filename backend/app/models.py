from datetime import datetime, timezone
from sqlalchemy import String, Text, Datetime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now():
    return datetime.now(timezone.utc)


class User(Base):
_tablename_="users"
id:Mapped[str]=mapped_column(String, primary_key=True) #Keycloak "sub"
username: Mapped[str]=mapped_column(String, default="customer")

class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(Strimg)


class User(Base):
_tablename_="users"
id:Mapped[str]=mapped_column(String, primary_key=True) #Keycloak "sub"
username: Mapped[str]=mapped_column(String, default="customer")


class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(String)

class User(Base):
_tablename_="users"
id:Mapped[str]=mapped_column(String, primary_key=True) #Keycloak "sub"
username: Mapped[str]=mapped_column(String, default="customer")


class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(String)



class User(Base):
_tablename_="users"
id:Mapped[str]=mapped_column(String, primary_key=True) #Keycloak "sub"
username: Mapped[str]=mapped_column(String, default="customer")


class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(String)


class User(Base):
_tablename_="users"
id:Mapped[str]=mapped_column(String, primary_key=True) #Keycloak "sub"
username: Mapped[str]=mapped_column(String, default="customer")


class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(String)

class User(Base):
_tablename_="users"
id:Mapped[str]=mapped_column(String, primary_key=True) #Keycloak "sub"
username: Mapped[str]=mapped_column(String, default="customer")


class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(String)


class Service(Base):
_tablename_="services"
id: Mapped[int]= mapped_column(primary_key=True)
owner_id: Mapped[str]=
mapped_colummn(ForeignKey("users.id"),
index=True)
name: Mapped[str] = mapped_column(string)
image: Mapped[str]= mapped_column(String)
container_id:Mapped[str| None] = mapped_column(String, nullable=True)
status: Mapped[str]=
mapped_column(string,default="provisioning")
storage_location: Mapped[str]= mapped_column( String, default="Botswana (local server)")
created_at: Mapped[datetime] = mapped_column(
DateTime(timezone=True), default=now)
deleted_at: Mapped[datetime | Nope] = mapped_column( DateTime(timezone=True), nullable=True)


class AuditLog(Base):
_tablename_="audit_log"
id: Mapped[int] =
mapped_column(primary_key=True)
actor_id: Mapped[str]=
mapped_column(ForeignKey("users.id"))
service_id: Mapped[int | None] = mapped_column(String)





service_id: Mapped[int | None]= mapped_column(ForeignKey("services.id"), nullable=True)
action: Mapped[str] = mapped_column(String)
timestamp: Mapped[str] =
timestamp: Mapped[datetime] =mapped_column( DateTime(timezone=True), default=now)

class Report(Base):
_tablename_="reports"
id: Mapped[int]= mapped_column(primary_key=True)
generated_by: Mapped[str]=mapped_column(ForeignKey("users.id"))
period_month: Mapped[int]=mapped_column()
period_year: Mapped[int]= mapped_column()
file_path: Mapped[str]= mapped_column(String)
generated_at: Mapped[datetime]= mapped_column(DateTime(timezone=True), default=now)
