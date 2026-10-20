import logging
import secrets
from datetime import datetime, timezone

import docker
from docker.errors import DockerException, NotFound
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import current_user, require_admin
from .database import SessionLocal, get_db
from .models import AuditLog, Service, User

log = logging.getLogger("uvicorn.error")
router = APIRouter()

# Images the platform may start. None = random value generated per service.
ALLOWED_IMAGES = {
    "nginx:alpine": {},
    "redis:alpine": {},
    "postgres:16": {"POSTGRES_PASSWORD": None},
}

STATE_MAP = {
    "running": "running", "restarting": "running", "created": "provisioning",
    "paused": "stopped", "exited": "stopped", "dead": "error",
}


class ServiceCreate(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9-]{3,30}$")
    image: str


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    image: str
    status: str
    storage_location: str
    created_at: datetime


class AuditOut(BaseModel):
    timestamp: datetime
    actor: str
    action: str
    resource: str


def provision(service_id: int):
    """Background job: start the container and record the result."""
    db = SessionLocal()
    try:
        svc = db.get(Service, service_id)
        if svc is None or svc.deleted_at is not None:
            return
        try:
            env = {k: v or secrets.token_urlsafe(16)
                   for k, v in ALLOWED_IMAGES[svc.image].items()}
            container = docker.from_env().containers.run(
                svc.image,
                detach=True,
                name=f"svc-{svc.id}-{svc.name}",
                environment=env,
                mem_limit="256m",
                labels={"cloudplatform.managed": "true",
                        "cloudplatform.owner": svc.owner_id},
            )
            svc.container_id = container.id
            svc.status = "running"
        except Exception:
            log.exception("Provisioning failed for service %s", service_id)
            svc.status = "error"
        db.commit()
    finally:
        db.close()


def refresh_status(services, db: Session):
    """Compare each record with its real container and update the status."""
    try:
        client = docker.from_env()
    except DockerException:
        return
    changed = False
    for svc in services:
        if not svc.container_id:
            continue
        try:
            state = client.containers.get(svc.container_id).status
            new = STATE_MAP.get(state, svc.status)
        except NotFound:
            new = "error"
        except DockerException:
            continue
        if new != svc.status:
            svc.status = new
            changed = True
    if changed:
        db.commit()


@router.get("/services", response_model=list[ServiceOut])
def list_services(user: User = Depends(current_user),
                  db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Service)
        .where(Service.owner_id == user.id, Service.deleted_at.is_(None))
        .order_by(Service.id)
    ).all()
    refresh_status(rows, db)
    return [ServiceOut.model_validate(r) for r in rows]


@router.post("/services", response_model=ServiceOut, status_code=201)
def create_service(body: ServiceCreate, background: BackgroundTasks,
                   user: User = Depends(require_admin),
                   db: Session = Depends(get_db)):
    if body.image not in ALLOWED_IMAGES:
        raise HTTPException(400, "Image not allowed")
    svc = Service(owner_id=user.id, name=body.name, image=body.image)
    db.add(svc)
    db.flush()  # gives the new record its id
    db.add(AuditLog(actor_id=user.id, service_id=svc.id, action="CREATE",
                    resource=f"service:{svc.name}"))
    db.commit()  # record and audit entry are saved together
    background.add_task(provision, svc.id)
    return ServiceOut.model_validate(svc)


@router.delete("/services/{service_id}", status_code=204)
def delete_service(service_id: int, user: User = Depends(require_admin),
                   db: Session = Depends(get_db)):
    svc = db.scalar(select(Service).where(
        Service.id == service_id,
        Service.owner_id == user.id,
        Service.deleted_at.is_(None)))
    if svc is None:
        raise HTTPException(404, "Service not found")
    if svc.container_id:
        try:
            docker.from_env().containers.get(svc.container_id).remove(force=True)
        except NotFound:
            pass
        except DockerException:
            raise HTTPException(502, "Could not remove the container")
    svc.deleted_at = datetime.now(timezone.utc)
    svc.status = "stopped"
    db.add(AuditLog(actor_id=user.id, service_id=svc.id, action="DELETE",
                    resource=f"service:{svc.name}"))
    db.commit()


@router.get("/audit", response_model=list[AuditOut])
def list_audit(limit: int = 200, _: User = Depends(require_admin),
               db: Session = Depends(get_db)):
    rows = db.execute(
        select(AuditLog, User.username)
        .join(User, User.id == AuditLog.actor_id)
        .order_by(AuditLog.id.desc())
        .limit(min(limit, 1000))
    ).all()
    return [AuditOut(timestamp=a.timestamp, actor=name,
                     action=a.action, resource=a.resource)
            for a, name in rows]
