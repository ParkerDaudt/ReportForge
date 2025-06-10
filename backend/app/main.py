import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "/data/attachments")
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

app = FastAPI(title="Pentest Reporting Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Pentest Reporting Tool Backend is running."}

# --- Projects ---
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)

@app.get("/projects/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db, skip=skip, limit=limit)

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_id, project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.delete_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# --- Findings ---
@app.post("/findings/", response_model=schemas.Finding)
def create_finding(finding: schemas.FindingCreate, db: Session = Depends(get_db)):
    return crud.create_finding(db, finding)

@app.get("/findings/{finding_id}", response_model=schemas.Finding)
def read_finding(finding_id: int, db: Session = Depends(get_db)):
    db_finding = crud.get_finding(db, finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return db_finding

@app.get("/projects/{project_id}/findings", response_model=list[schemas.Finding])
def read_project_findings(project_id: int, db: Session = Depends(get_db)):
    return crud.get_findings_by_project(db, project_id)

@app.put("/findings/{finding_id}", response_model=schemas.Finding)
def update_finding(finding_id: int, finding: schemas.FindingUpdate, db: Session = Depends(get_db)):
    db_finding = crud.update_finding(db, finding_id, finding)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return db_finding

@app.delete("/findings/{finding_id}", response_model=schemas.Finding)
def delete_finding(finding_id: int, db: Session = Depends(get_db)):
    db_finding = crud.delete_finding(db, finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return db_finding

# --- Tags ---
@app.post("/tags/", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    return crud.create_tag(db, tag)

@app.get("/tags/", response_model=list[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tags(db, skip=skip, limit=limit)

@app.put("/tags/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag: schemas.TagUpdate, db: Session = Depends(get_db)):
    db_tag = crud.update_tag(db, tag_id, tag)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@app.delete("/tags/{tag_id}", response_model=schemas.Tag)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = crud.delete_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

# --- Simple Audit Log endpoint ---
@app.post("/audit/", response_model=schemas.AuditLog)
def create_audit_log(log: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    return crud.create_audit_log(db, log)

# --- Attachments ---

@app.post("/findings/{finding_id}/attachments", response_model=schemas.Attachment)
def upload_attachment(finding_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_finding = crud.get_finding(db, finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    filename = file.filename
    save_name = f"{finding_id}_{filename}"
    save_path = os.path.join(ATTACHMENTS_DIR, save_name)
    with open(save_path, "wb") as f:
        f.write(file.file.read())
    # Save attachment to db
    from .models import Attachment
    db_attachment = Attachment(
        finding_id=finding_id,
        filename=filename,
        filepath=save_path
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

@app.get("/findings/{finding_id}/attachments", response_model=list[schemas.Attachment])
def list_attachments(finding_id: int, db: Session = Depends(get_db)):
    db_finding = crud.get_finding(db, finding_id)
    if db_finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return db_finding.attachments

@app.get("/attachments/{attachment_id}/download")
def download_attachment(attachment_id: int, db: Session = Depends(get_db)):
    attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()
    if attachment is None or not os.path.exists(attachment.filepath):
        raise HTTPException(status_code=404, detail="Attachment not found")
    return FileResponse(
        path=attachment.filepath,
        filename=attachment.filename,
        media_type="application/octet-stream"
    )