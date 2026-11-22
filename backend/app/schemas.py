from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: str

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

class FindingUpdate(BaseModel):
    name: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    cve: Optional[str] = None
    cwe: Optional[str] = None
    cvss: Optional[float] = None
    affected_host: Optional[str] = None
    status: Optional[str] = None
    recommendation: Optional[str] = None
    evidence: Optional[str] = None
    references: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    tag_ids: Optional[List[int]] = None

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
    project_metadata: Optional[str] = None  # Renamed from 'metadata'

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    assessment_dates: Optional[str] = None
    scope: Optional[str] = None
    team_members: Optional[str] = None
    project_metadata: Optional[str] = None  # Renamed from 'metadata'

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

# --- Master Finding Schemas ---

from typing import List

class MasterFindingBase(BaseModel):
    title: str
    technical_analysis: str = ""
    impact: str = ""
    frameworks: List[str] = []
    recommendations: str = ""
    references: str = ""

class MasterFindingCreate(MasterFindingBase):
    pass

class MasterFindingUpdate(BaseModel):
    title: str | None = None
    technical_analysis: str | None = None
    impact: str | None = None
    frameworks: List[str] | None = None
    recommendations: str | None = None
    references: str | None = None

class MasterFinding(MasterFindingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Scheduled Export and AuditLogOut Schemas ---

class ScheduledExportBase(BaseModel):
    project_id: int
    template_id: int
    frequency: str  # daily, weekly, monthly
    active: bool = True

class ScheduledExportCreate(ScheduledExportBase):
    pass

class ScheduledExport(ScheduledExportBase):
    id: int
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    created_at: datetime
    class Config:
        orm_mode = True

class AuditLogOut(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int
    user: Optional[str]
    timestamp: datetime
    details: Optional[str]
    class Config:
        orm_mode = True