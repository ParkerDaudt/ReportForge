from sqlalchemy.orm import Session
from . import models, schemas

# --- Project CRUD ---
def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# --- Finding CRUD ---
def get_finding(db: Session, finding_id: int):
    return db.query(models.Finding).filter(models.Finding.id == finding_id).first()

def get_findings_by_project(db: Session, project_id: int):
    return db.query(models.Finding).filter(models.Finding.project_id == project_id).all()

def create_finding(db: Session, finding: schemas.FindingCreate):
    tag_objs = db.query(models.Tag).filter(models.Tag.id.in_(finding.tag_ids)).all()
    db_finding = models.Finding(
        **finding.dict(exclude={"tag_ids"}),
        tags=tag_objs
    )
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding

# --- Tag CRUD ---
def get_tag(db: Session, tag_id: int):
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).offset(skip).limit(limit).all()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# --- AuditLog (simplified for now) ---
def create_audit_log(db: Session, log: schemas.AuditLogCreate):
    db_log = models.AuditLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log