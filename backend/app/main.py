import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi import Form
from typing import Optional
import shutil
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "/data/attachments")
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "/data/templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

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

# --- Report Templates ---

@app.post("/report-templates/", response_model=schemas.ReportTemplate)
def upload_report_template(
    name: str = Form(...),
    type: str = Form(...),  # docx/html/md
    description: Optional[str] = Form(None),
    is_sample: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename
    save_name = f"{name}_{filename}"
    save_path = os.path.join(TEMPLATES_DIR, save_name)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # Save template metadata to db
    from .models import ReportTemplate
    db_template = ReportTemplate(
        name=name,
        type=type,
        description=description,
        is_sample=is_sample,
        file_path=save_path,
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@app.get("/report-templates/", response_model=list[schemas.ReportTemplate])
def list_report_templates(db: Session = Depends(get_db)):
    return db.query(models.ReportTemplate).all()

@app.get("/report-templates/samples", response_model=list[schemas.ReportTemplate])
def list_sample_templates(db: Session = Depends(get_db)):
    return db.query(models.ReportTemplate).filter(models.ReportTemplate.is_sample == True).all()

@app.get("/report-templates/{template_id}/download")
def download_report_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(models.ReportTemplate).filter(models.ReportTemplate.id == template_id).first()
    if template is None or not os.path.exists(template.file_path):
        raise HTTPException(status_code=404, detail="Template not found")
    ext = template.type if template.type in ["docx", "md", "html"] else "bin"
    media_type = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "md": "text/markdown",
        "html": "text/html"
    }.get(ext, "application/octet-stream")
    return FileResponse(
        path=template.file_path,
        filename=os.path.basename(template.file_path),
        media_type=media_type
    )

@app.delete("/report-templates/{template_id}", response_model=schemas.ReportTemplate)
def delete_report_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(models.ReportTemplate).filter(models.ReportTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    # Delete file from disk
    if os.path.exists(template.file_path):
        os.remove(template.file_path)
    db.delete(template)
    db.commit()
    return template

# --- Sample Data Seeding ---

def seed_sample_data(db: Session):
    # Create tags
    tag_web = models.Tag(name="Web")
    tag_infra = models.Tag(name="Infrastructure")
    db.add_all([tag_web, tag_infra])
    db.commit()
    db.refresh(tag_web)
    db.refresh(tag_infra)

    # Create project
    project = models.Project(
        name="Demo Pentest Engagement",
        client="Acme Corp",
        assessment_dates="2024-06-01 to 2024-06-07",
        scope="Web application and public infrastructure",
        team_members="Alice, Bob",
        metadata="Sample engagement"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Create findings
    finding1 = models.Finding(
        project_id=project.id,
        name="SQL Injection in Login Form",
        severity="Critical",
        description="SQL injection vulnerability was discovered in the login form.",
        cve="CVE-2022-1234",
        cwe="CWE-89",
        cvss=9.8,
        affected_host="app.acme.com",
        status="draft",
        recommendation="Use parameterized queries and input validation.",
        evidence="Screenshot attached.",
        references="https://owasp.org/www-community/attacks/SQL_Injection",
        notes="Manual test confirmed using sqlmap.",
        category="Web",
        tags=[tag_web]
    )
    finding2 = models.Finding(
        project_id=project.id,
        name="Outdated OpenSSH Version",
        severity="Medium",
        description="OpenSSH version is outdated and affected by known vulnerabilities.",
        cve="CVE-2020-15778",
        cwe="CWE-119",
        cvss=6.5,
        affected_host="infra.acme.com",
        status="draft",
        recommendation="Upgrade OpenSSH to the latest supported version.",
        evidence="Banner grab shows OpenSSH_7.2p2.",
        references="https://nvd.nist.gov/vuln/detail/CVE-2020-15778",
        notes="",
        category="Infrastructure",
        tags=[tag_infra]
    )
    db.add_all([finding1, finding2])
    db.commit()

    # Add a sample DOCX template
    docx_template_path = os.path.join(TEMPLATES_DIR, "sample_report.docx")
    with open(docx_template_path, "wb") as f:
        f.write(b"PK\x03\x04Sample DOCX template placeholder\x00\x00")  # not a real docx
    db_template_docx = models.ReportTemplate(
        name="Sample DOCX Report",
        type="docx",
        description="Sample pentest report template (DOCX)",
        is_sample=True,
        file_path=docx_template_path
    )
    # Add a sample Markdown template
    markdown_template_path = os.path.join(TEMPLATES_DIR, "sample_report.md")
    with open(markdown_template_path, "w") as f:
        f.write("# Pentest Report\n\n## Findings\n\n{{findings}}\n")
    db_template_md = models.ReportTemplate(
        name="Sample Markdown Report",
        type="md",
        description="Sample pentest report template (Markdown)",
        is_sample=True,
        file_path=markdown_template_path
    )
    db.add_all([db_template_docx, db_template_md])
    db.commit()

@app.post("/seed-sample-data")
def seed_sample_endpoint(db: Session = Depends(get_db)):
    seed_sample_data(db)
    return {"status": "Sample data seeded"}