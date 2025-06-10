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

# --- MasterFinding CRUD ---

def get_master_finding(db: Session, finding_id: int):
    return db.query(models.MasterFinding).filter(models.MasterFinding.id == finding_id).first()

def get_master_findings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MasterFinding).offset(skip).limit(limit).all()

def create_master_finding(db: Session, finding: schemas.MasterFindingCreate):
    db_finding = models.MasterFinding(
        title=finding.title,
        technical_analysis=finding.technical_analysis,
        impact=finding.impact,
        frameworks=",".join(finding.frameworks),
        recommendations=finding.recommendations,
        references=finding.references,
    )
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding

def update_master_finding(db: Session, finding_id: int, finding_update: schemas.MasterFindingUpdate):
    db_finding = get_master_finding(db, finding_id)
    if not db_finding:
        return None
    data = finding_update.dict(exclude_unset=True)
    if "frameworks" in data and data["frameworks"] is not None:
        db_finding.frameworks = ",".join(data["frameworks"])
        data.pop("frameworks")
    for field, value in data.items():
        setattr(db_finding, field, value)
    db.commit()
    db.refresh(db_finding)
    return db_finding

def delete_master_finding(db: Session, finding_id: int):
    db_finding = get_master_finding(db, finding_id)
    if not db_finding:
        return None
    db.delete(db_finding)
    db.commit()
    return db_finding

# --- Scheduled Export CRUD ---

def get_scheduled_exports(db: Session):
    return db.query(models.ScheduledExport).all()

def create_scheduled_export(db: Session, se: schemas.ScheduledExportCreate):
    db_se = models.ScheduledExport(
        project_id=se.project_id,
        template_id=se.template_id,
        frequency=se.frequency,
        active=se.active,
    )
    db.add(db_se)
    db.commit()
    db.refresh(db_se)
    return db_se

def delete_scheduled_export(db: Session, se_id: int):
    se = db.query(models.ScheduledExport).filter(models.ScheduledExport.id == se_id).first()
    if not se:
        return None
    db.delete(se)
    db.commit()
    return se

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()