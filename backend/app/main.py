import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi import Form
from typing import Optional
import shutil
import tempfile
from jinja2 import Template as JinjaTemplate
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .parsers import burp, nessus
from typing import List
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

# --- Report Export Endpoint ---

@app.post("/export-report/")
def export_report(
    project_id: int = Form(...),
    template_id: int = Form(...),
    output_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Generate and download a report for a project using the selected template.
    """
    # Look up project and findings
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    findings = crud.get_findings_by_project(db, project_id)
    # Look up template
    template = db.query(models.ReportTemplate).filter(models.ReportTemplate.id == template_id).first()
    if not template or not os.path.exists(template.file_path):
        raise HTTPException(status_code=404, detail="Template not found")
    tpl_type = output_type or template.type

    # Prepare context
    context = {
        "project": {
            "name": project.name,
            "client": project.client,
            "assessment_dates": project.assessment_dates,
            "scope": project.scope,
            "team_members": project.team_members,
            "metadata": project.metadata,
        },
        "findings": [
            {
                "name": f.name,
                "severity": f.severity,
                "description": f.description,
                "cve": f.cve,
                "cwe": f.cwe,
                "cvss": f.cvss,
                "affected_host": f.affected_host,
                "status": f.status,
                "recommendation": f.recommendation,
                "evidence": f.evidence,
                "references": f.references,
                "notes": f.notes,
                "category": f.category,
                "tags": [t.name for t in f.tags],
            } for f in findings
        ]
    }

    # Markdown/HTML export using Jinja2
    if tpl_type in ("md", "html"):
        with open(template.file_path, "r") as f:
            tpl_content = f.read()
        # If template uses {{findings}}, render finding sections/table
        if "{{findings}}" in tpl_content:
            findings_md = ""
            for f in context["findings"]:
                findings_md += (
                    f"### {f['name']}\n"
                    f"- Severity: {f['severity']}\n"
                    f"- CVE: {f['cve']}\n"
                    f"- CVSS: {f['cvss']}\n"
                    f"- CWE: {f['cwe']}\n"
                    f"- Affected Host: {f['affected_host']}\n"
                    f"- Status: {f['status']}\n"
                    f"- Tags: {', '.join(f['tags'])}\n"
                    f"- Category: {f['category']}\n\n"
                    f"**Description:** {f['description']}\n\n"
                    f"**Recommendation:** {f['recommendation']}\n\n"
                    f"**Evidence:** {f['evidence']}\n\n"
                    f"**References:** {f['references']}\n\n"
                    f"**Notes:** {f['notes']}\n\n"
                    "----\n\n"
                )
            context["findings_md"] = findings_md
            tpl_content = tpl_content.replace("{{findings}}", "{{findings_md}}")
        rendered = JinjaTemplate(tpl_content).render(**context)
        ext = "md" if tpl_type == "md" else "html"
        content_type = "text/markdown" if ext == "md" else "text/html"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
        tmp.write(rendered.encode("utf-8"))
        tmp.close()
        return FileResponse(
            path=tmp.name,
            filename=f"{project.name}_report.{ext}",
            media_type=content_type
        )

    # DOCX export (stub if real docx template not present)
    elif tpl_type == "docx":
        try:
            from docxtpl import DocxTemplate
            doc = DocxTemplate(template.file_path)
            # For findings, flatten as a string for now
            findings_text = ""
            for f in context["findings"]:
                findings_text += (
                    f"Finding: {f['name']}\n"
                    f"Severity: {f['severity']}\n"
                    f"CVE: {f['cve']}\n"
                    f"CVSS: {f['cvss']}\n"
                    f"CWE: {f['cwe']}\n"
                    f"Affected Host: {f['affected_host']}\n"
                    f"Status: {f['status']}\n"
                    f"Tags: {', '.join(f['tags'])}\n"
                    f"Category: {f['category']}\n"
                    f"Description: {f['description']}\n"
                    f"Recommendation: {f['recommendation']}\n"
                    f"Evidence: {f['evidence']}\n"
                    f"References: {f['references']}\n"
                    f"Notes: {f['notes']}\n"
                    "-----------------------------\n"
                )
            context["findings"] = findings_text
            doc.render(context)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
            doc.save(tmp.name)
            tmp.close()
            return FileResponse(
                path=tmp.name,
                filename=f"{project.name}_report.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except ImportError:
            # Fallback: just send the template itself
            return FileResponse(
                path=template.file_path,
                filename=f"{project.name}_report.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    else:
        raise HTTPException(status_code=400, detail="Unsupported template/report type")

# --- Sample Data Seeding ---

def seed_sample_data(db: Session):
    # Create tags
    tag_web = models.Tag(name="Web")
    tag_infra = models.Tag(name="Infrastructure")
    db.add_all([tag_web, tag_infra])
    db.commit()
    db.refresh(tag_web)
    db.refresh(tag_infra)
    # ... rest unchanged

@app.post("/seed-sample-data")
def seed_sample_endpoint(db: Session = Depends(get_db)):
    seed_sample_data(db)
    return {"status": "Sample data seeded"}

# --- Master Findings Endpoints ---

@app.post("/master-findings/", response_model=schemas.MasterFinding)
def create_master_finding(finding: schemas.MasterFindingCreate, db: Session = Depends(get_db)):
    return crud.create_master_finding(db, finding)

@app.get("/master-findings/", response_model=List[schemas.MasterFinding])
def list_master_findings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_master_findings(db, skip=skip, limit=limit)

@app.get("/master-findings/{finding_id}", response_model=schemas.MasterFinding)
def get_master_finding(finding_id: int, db: Session = Depends(get_db)):
    db_finding = crud.get_master_finding(db, finding_id)
    if not db_finding:
        raise HTTPException(status_code=404, detail="Master finding not found")
    # Convert frameworks string to list for API
    mf_dict = db_finding.__dict__.copy()
    mf_dict["frameworks"] = db_finding.frameworks.split(",") if db_finding.frameworks else []
    return schemas.MasterFinding(**mf_dict)

@app.put("/master-findings/{finding_id}", response_model=schemas.MasterFinding)
def update_master_finding(finding_id: int, finding: schemas.MasterFindingUpdate, db: Session = Depends(get_db)):
    db_finding = crud.update_master_finding(db, finding_id, finding)
    if not db_finding:
        raise HTTPException(status_code=404, detail="Master finding not found")
    mf_dict = db_finding.__dict__.copy()
    mf_dict["frameworks"] = db_finding.frameworks.split(",") if db_finding.frameworks else []
    return schemas.MasterFinding(**mf_dict)

@app.delete("/master-findings/{finding_id}", response_model=schemas.MasterFinding)
def delete_master_finding(finding_id: int, db: Session = Depends(get_db)):
    db_finding = crud.delete_master_finding(db, finding_id)
    if not db_finding:
        raise HTTPException(status_code=404, detail="Master finding not found")
    mf_dict = db_finding.__dict__.copy()
    mf_dict["frameworks"] = db_finding.frameworks.split(",") if db_finding.frameworks else []
    return schemas.MasterFinding(**mf_dict)

# --- Tool Import Endpoints ---

@app.post("/import-tool/")
def import_tool(
    file: UploadFile = File(...),
    tool: str = Form(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Import findings from a tool (Burp or Nessus for now) and add to the DB under the given project.
    """
    content = file.file.read()
    if tool.lower() == "burp":
        findings = burp.parse_burp_xml(content)
        default_category = "Web"
    elif tool.lower() == "nessus":
        findings = nessus.parse_nessus_xml(content)
        default_category = "Infrastructure"
    else:
        raise HTTPException(status_code=400, detail="Unsupported tool type")

    # Ensure project exists
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure category tag exists
    tag_name = default_category
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        tag = models.Tag(name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    
    added = 0
    for f in findings:
        # Deduplication logic: skip if name+affected_host already exists for project
        exists = db.query(models.Finding).filter(
            models.Finding.project_id == project_id,
            models.Finding.name == f["name"],
            models.Finding.affected_host == f["affected_host"]
        ).first()
        if exists:
            continue
        db_finding = models.Finding(
            project_id=project_id,
            name=f["name"],
            severity=f.get("severity") or "Info",
            description=f.get("description"),
            cve=f.get("cve"),
            cwe=f.get("cwe"),
            cvss=f.get("cvss"),
            affected_host=f.get("affected_host"),
            status=f.get("status") or "draft",
            recommendation=f.get("recommendation"),
            evidence=f.get("evidence"),
            references=f.get("references"),
            notes="Imported from tool",
            category=f.get("category") or tag_name,
            tags=[tag]
        )
        db.add(db_finding)
        added += 1
    db.commit()
    return {"imported": added}