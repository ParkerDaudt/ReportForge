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

def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate):
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    for field, value in project_update.dict(exclude_unset=True).items():
        setattr(db_project, field, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    db.delete(db_project)
    db.commit()
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

def update_finding(db: Session, finding_id: int, finding_update: schemas.FindingUpdate):
    db_finding = get_finding(db, finding_id)
    if not db_finding:
        return None
    data = finding_update.dict(exclude_unset=True)
    # Handle tag updates
    if "tag_ids" in data:
        tag_objs = db.query(models.Tag).filter(models.Tag.id.in_(data["tag_ids"])).all()
        db_finding.tags = tag_objs
        data.pop("tag_ids")
    for field, value in data.items():
        setattr(db_finding, field, value)
    db.commit()
    db.refresh(db_finding)
    return db_finding

def delete_finding(db: Session, finding_id: int):
    db_finding = get_finding(db, finding_id)
    if not db_finding:
        return None
    db.delete(db_finding)
    db.commit()
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

def update_tag(db: Session, tag_id: int, tag_update: schemas.TagUpdate):
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return None
    for field, value in tag_update.dict(exclude_unset=True).items():
        setattr(db_tag, field, value)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, tag_id: int):
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return None
    db.delete(db_tag)
    db.commit()
    return db_tag

# --- AuditLog (simplified for now) ---
def create_audit_log(db: Session, log: schemas.AuditLogCreate):
    db_log = models.AuditLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log