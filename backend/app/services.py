import base64
import html
import logging
import os
from datetime import datetime, timezone

import docker
from docker.errors import DockerException, NotFound
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import current_user, require_admin
from .database import SessionLocal, get_db
from .models import AuditLog, Service, User

load_dotenv()
log = logging.getLogger("uvicorn.error")
router = APIRouter()

PUBLIC_HOST = os.environ.get("PUBLIC_HOST", "localhost")
PORT_MIN, PORT_MAX = 8100, 8199

# Web images the platform may start, and where each one serves its pages.
ALLOWED_IMAGES = {
    "nginx:alpine": {"port": 80, "webroot": "/usr/share/nginx/html"},
    "httpd:alpine": {"port": 80, "webroot": "/usr/local/apache2/htdocs"},
}

STATE_MAP = {
    "running": "running", "restarting": "running", "created": "provisioning",
    "paused": "stopped", "exited": "stopped", "dead": "error",
}


class ServiceCreate(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9-]{3,30}$")
    image: str
    owner_id: str | None = None


class ServiceOut(BaseModel):
    id: int
    name: str
    owner: str
    image: str
    status: str
    storage_location: str
    port: int | None
    url: str | None
    created_at: datetime


class AuditOut(BaseModel):
    timestamp: datetime
    actor: str
    action: str
    resource: str


class CustomerOut(BaseModel):
    id: str
    username: str


def to_out(svc: Service, owner_name: str) -> ServiceOut:
    url = f"http://{PUBLIC_HOST}:{svc.port}" if svc.port else None
    return ServiceOut(
        id=svc.id, name=svc.name, owner=owner_name, image=svc.image,
        status=svc.status, storage_location=svc.storage_location,
        port=svc.port, url=url, created_at=svc.created_at)


def free_port(db: Session) -> int:
    used = set(db.scalars(
        select(Service.port).where(
            Service.port.is_not(None), Service.deleted_at.is_(None))
    ).all())
    for p in range(PORT_MIN, PORT_MAX + 1):
        if p not in used:
            return p
    raise HTTPException(503, "No free ports left")


def welcome_page(svc: Service, owner_name: str) -> str:
    name = html.escape(svc.name)
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f"<title>{name}</title></head>"
        '<body style="font-family:Arial,sans-serif;max-width:640px;'
        'margin:60px auto;padding:0 16px;color:#1f2933">'
        f"<h1>{name} is running</h1>"
        "<p>This service is hosted on the local cloud platform.</p>"
        f"<p><b>Owner:</b> {html.escape(owner_name)}<br>"
        f"<b>Image:</b> {html.escape(svc.image)}<br>"
        f"<b>Storage location:</b> {html.escape(svc.storage_location)}</p>"
        "</body></html>"
    )


def write_page(container, svc: Service, owner_name: str):
    root = ALLOWED_IMAGES[svc.image]["webroot"]
    payload = base64.b64encode(welcome_page(svc, owner_name).encode()).decode()
    container.exec_run(
        ["sh", "-c", f"echo '{payload}' | base64 -d > {root}/index.html"])


def provision(service_id: int):
    """Background job: start the container and record the result."""
    db = SessionLocal()
    try:
        svc = db.get(Service, service_id)
        if svc is None or svc.deleted_at is not None:
            return
        owner = db.get(User, svc.owner_id)
        owner_name = owner.username if owner else "unknown"
        spec = ALLOWED_IMAGES[svc.image]
        try:
            container = docker.from_env().containers.run(
                svc.image,
                detach=True,
                name=f"svc-{svc.id}-{svc.name}",
                ports={f"{spec['port']}/tcp": svc.port},
                mem_limit="256m",
                labels={"cloudplatform.managed": "true",
                        "cloudplatform.owner": svc.owner_id},
            )
            svc.container_id = container.id
            svc.status = "running"
            try:
                write_page(container, svc, owner_name)
            except Exception:
                log.exception("Could not write page for service %s", service_id)
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
    query = (
        select(Service, User.username)
        .join(User, User.id == Service.owner_id)
        .where(Service.deleted_at.is_(None))
        .order_by(Service.id)
    )
    if user.role != "admin":
        query = query.where(Service.owner_id == user.id)
    rows = db.execute(query).all()
    refresh_status([svc for svc, _ in rows], db)
    return [to_out(svc, name) for svc, name in rows]


@router.post("/services", response_model=ServiceOut, status_code=201)
def create_service(body: ServiceCreate, background: BackgroundTasks,
                   user: User = Depends(require_admin),
                   db: Session = Depends(get_db)):
    if body.image not in ALLOWED_IMAGES:
        raise HTTPException(400, "Image not allowed")
    owner = user
    if body.owner_id:
        owner = db.get(User, body.owner_id)
        if owner is None or owner.role != "customer":
            raise HTTPException(
                400, "Owner must be a customer who has logged in")
    svc = Service(owner_id=owner.id, name=body.name, image=body.image,
                  port=free_port(db))
    db.add(svc)
    db.flush()  # gives the new record its id
    db.add(AuditLog(actor_id=user.id, service_id=svc.id, action="CREATE",
                    resource=f"service:{svc.name} (owner: {owner.username})"))
    db.commit()  # record and audit entry are saved together
    background.add_task(provision, svc.id)
    return to_out(svc, owner.username)


@router.delete("/services/{service_id}", status_code=204)
def delete_service(service_id: int, user: User = Depends(require_admin),
                   db: Session = Depends(get_db)):
    svc = db.scalar(select(Service).where(
        Service.id == service_id, Service.deleted_at.is_(None)))
    if svc is None:
        raise HTTPException(404, "Service not found")
    if svc.container_id:
        try:
            docker.from_env().containers.get(svc.container_id).remove(force=True)
        except NotFound:
            pass
        except DockerException:
            raise HTTPException(502, "Could not remove the container")
    owner = db.get(User, svc.owner_id)
    owner_name = owner.username if owner else "unknown"
    svc.deleted_at = datetime.now(timezone.utc)
    svc.status = "stopped"
    db.add(AuditLog(actor_id=user.id, service_id=svc.id, action="DELETE",
                    resource=f"service:{svc.name} (owner: {owner_name})"))
    db.commit()


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(_: User = Depends(require_admin),
                   db: Session = Depends(get_db)):
    rows = db.scalars(
        select(User).where(User.role == "customer").order_by(User.username)
    ).all()
    return [CustomerOut(id=u.id, username=u.username) for u in rows]


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
