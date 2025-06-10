from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

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