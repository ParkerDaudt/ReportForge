# Pentest Reporting Tool

A modern, offline-first, extensible penetration testing reporting and workflow platform.  
Built with FastAPI (Python) backend and React + Mantine frontend. Fully Dockerized for easy local deployment.

---

## Features

- **Multi-tool Import:** Ingest scan results from Burp Suite, Nessus, Nmap, Qualys, OpenVAS, Nikto (XML/JSON/HTML).
- **Manual Findings:** Browser-based rich entry/edit of findings, with file/screenshot support.
- **Projects & Engagements:** Track multiple assessments, clients, scope, and team members.
- **Master Findings Library:** Central, reusable technical finding database with NIST/MITRE mappings. Clone entries into projects.
- **CRUD Everywhere:** Projects, Findings (per project), Tags, Attachments, Templates, Master Findings all have full create, read, update, delete UI and API.
- **Attachments:** Upload, download, and manage evidence and screenshots per finding.
- **Tagging & Categorization:** Tag findings for easy filtering and organization.
- **Customizable Reporting:** Templating system supports DOCX, Markdown, and HTML (with placeholder variables and live preview).
- **Export/Generate Reports:** Download ready-to-share reports (Markdown, HTML, DOCX) for any project using any template.
- **Import/Export UI:** Drag-and-drop scan import, project/template selection for export.
- **Audit Log:** View all important actions/changes system-wide.
- **Recurring Report Scheduling:** Schedule exports for regular delivery (daily/weekly/monthly).
- **Backup & Restore:** Download/upload a ZIP archive of your database and attachments for easy backup/restore.
- **Minimalist UI:** Modern, dark-mode-enabled interface with search/filter, notifications, and live previews.
- **Deduplication & Auto-merge:** Deduplicate findings across multiple imports.
- **CVSS & CVE/NVD Integration:** Auto-fetch and score vulnerabilities, manual override supported.
- **API-first:** Fully documented OpenAPI endpoints for integration and automation.

---

## Getting Started

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/pentest-reporting-tool.git
   cd pentest-reporting-tool
   ```

2. **Start with Docker Compose:**
   ```sh
   docker-compose up --build
   ```

3. **Access the app:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API & docs: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Data and attachments** are stored in the `data/` directory (mounted as Docker volume).

---

## Development

- **Backend:** See [`backend/`](backend/)
- **Frontend:** See [`frontend/`](frontend/)

---

## Advanced Features

- **Audit Log Viewer:** See a history of changes and actions across the platform.
- **Scheduling:** Schedule and manage recurring report exports in the UI.
- **Backup/Restore:** Download/upload your entire workspace state (DB and attachments) as a ZIP.
- **Live Markdown/HTML Preview:** See instant previews of templates and generated reports.
- **Master Findings Library:** Quickly add previously documented issues to new projects.

---

## Roadmap

See issues and milestones for planned and requested features.

---

## Community and Contributions

Pull requests and suggestions are welcome!