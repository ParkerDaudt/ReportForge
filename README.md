# Pentest Reporting Tool

A modern, offline-first penetration testing reporting tool for managing, deduplicating, and generating security assessment findings and reports.  
Built with FastAPI (Python) backend and React + Mantine frontend, fully Dockerized.

---

## Features

- Import scan results from Burp, Nessus, Nmap, Qualys, OpenVAS, Nikto (and more)
- Manual finding entry with attachments
- Project/Engagement tracking
- Master findings database with deduplication
- Customizable, editable report templates (DOCX, PDF, HTML, Markdown)
- Auto-fetch CVE/NVD data, CVSS scoring (manual override)
- Minimalist, responsive UI with dark mode toggle
- Audit logging, scheduling, and more

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
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Data and attachments** are stored in the `data/` directory (mounted as Docker volume).

---

## Development

- **Backend:** See [`backend/`](backend/)
- **Frontend:** See [`frontend/`](frontend/)

## Roadmap

See issues and milestones for planned features.