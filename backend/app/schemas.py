from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        orm_mode = True

class AttachmentBase(BaseModel):
    filename: str

class AttachmentCreate(AttachmentBase):
    pass

class Attachment(AttachmentBase):
    id: int
    filepath: str
    uploaded_at: datetime
    class Config:
        orm_mode = True

class FindingBase(BaseModel):
    name: str
    severity: str
    description: Optional[str] = None
    cve: Optional[str] = None
    cwe: Optional[str] = None
    cvss: Optional[float] = None
    affected_host: Optional[str] = None
    status: Optional[str] = "draft"
    recommendation: Optional[str] = None
    evidence: Optional[str] = None
    references: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None

class FindingCreate(FindingBase):
    project_id: int
    tag_ids: List[int] = Field(default_factory=list)

class Finding(FindingBase):
    id: int
    project_id: int
    tags: List[Tag] = []
    attachments: List[Attachment] = []
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    client: Optional[str] = None
    assessment_dates: Optional[str] = None
    scope: Optional[str] = None
    team_members: Optional[str] = None
    metadata: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    findings: List[Finding] = []
    class Config:
        orm_mode = True

class ReportTemplateBase(BaseModel):
    name: str
    type: str  # docx/html/md
    description: Optional[str] = None

class ReportTemplateCreate(ReportTemplateBase):
    pass

class ReportTemplate(ReportTemplateBase):
    id: int
    file_path: str
    is_sample: bool
    uploaded_at: datetime
    class Config:
        orm_mode = True

class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: int
    user: Optional[str] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True