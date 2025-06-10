from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

# Association table for many-to-many finding <-> tags
finding_tags = Table(
    "finding_tags",
    Base.metadata,
    Column("finding_id", Integer, ForeignKey("findings.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client = Column(String, nullable=True)
    assessment_dates = Column(String, nullable=True)
    scope = Column(Text, nullable=True)
    team_members = Column(String, nullable=True)
    metadata = Column(Text, nullable=True)

    findings = relationship("Finding", back_populates="project", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cve = Column(String, nullable=True)
    cwe = Column(String, nullable=True)
    cvss = Column(Float, nullable=True)
    affected_host = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")
    recommendation = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="findings")
    tags = relationship("Tag", secondary=finding_tags, back_populates="findings")
    attachments = relationship("Attachment", back_populates="finding", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="finding", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    findings = relationship("Finding", secondary=finding_tags, back_populates="tags")

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    finding = relationship("Finding", back_populates="attachments")

class MasterFinding(Base):
    __tablename__ = "master_findings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    technical_analysis = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)
    frameworks = Column(String, nullable=True)  # Comma-separated NIST/MITRE IDs
    recommendations = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportTemplate(Base):
    __tablename__ = "report_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    type = Column(String, nullable=False)  # docx/html/md
    is_sample = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    user = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=True)

    finding = relationship("Finding", back_populates="audit_logs")