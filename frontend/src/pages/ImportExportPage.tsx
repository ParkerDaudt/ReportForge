import React, { useEffect, useState } from "react";
import api from "../api";
import {
  Tabs,
  Button,
  Group,
  FileInput,
  Select,
  Title,
  LoadingOverlay,
  Stack,
  Notification,
} from "@mantine/core";
import { IconUpload, IconDownload } from "@tabler/icons-react";

type Project = { id: number; name: string };
type Template = { id: number; name: string; type: string };

export function ImportExportPage() {
  // Import state
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importTool, setImportTool] = useState<string | null>(null);
  const [importProject, setImportProject] = useState<string | null>(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);

  // Export state
  const [exportProject, setExportProject] = useState<string | null>(null);
  const [exportTemplate, setExportTemplate] = useState<string | null>(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [exportUrl, setExportUrl] = useState<string | null>(null);

  useEffect(() => {
    api.get("/projects/").then((res) => setProjects(res.data));
    api.get("/report-templates/").then((res) => setTemplates(res.data));
  }, []);

  // Import handler
  const handleImport = async () => {
    if (!importFile || !importTool || !importProject) return;
    setImportLoading(true);
    setImportResult(null);
    const formData = new FormData();
    formData.append("file", importFile);
    formData.append("tool", importTool);
    formData.append("project_id", importProject);
    try {
      const res = await api.post("/import-tool/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setImportResult(`Imported findings: ${res.data.imported}`);
    } catch (err: any) {
      setImportResult(
        err?.response?.data?.detail
          ? `Error: ${err.response.data.detail}`
          : "Import failed."
      );
    } finally {
      setImportLoading(false);
    }
  };

  // Export handler
  const handleExport = async () => {
    if (!exportProject || !exportTemplate) return;
    setExportLoading(true);
    setExportUrl(null);
    const formData = new FormData();
    formData.append("project_id", exportProject);
    formData.append("template_id", exportTemplate);
    try {
      const res = await api.post("/export-report/", formData, {
        responseType: "blob",
      });
      // Create a download link:
      const contentDisposition = res.headers["content-disposition"];
      let filename = "report";
      if (contentDisposition) {
        const match = /filename="?([^"]+)"?/.exec(contentDisposition);
        if (match) filename = match[1];
      }
      const url = window.URL.createObjectURL(new Blob([res.data]));
      setExportUrl(url);
      // Optionally, auto-download:
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 2000);
    } catch (err: any) {
      alert(
        err?.response?.data?.detail
          ? `Error: ${err.response.data.detail}`
          : "Export failed."
      );
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <div style={{ position: "relative" }}>
      <Tabs defaultValue="import">
        <Tabs.List>
          <Tabs.Tab value="import" icon={<IconUpload size={16} />}>
            Import Tool Report
          </Tabs.Tab>
          <Tabs.Tab value="export" icon={<IconDownload size={16} />}>
            Export Report
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="import" pt="xl">
          <Stack>
            <Title order={4}>Import Tool Report</Title>
            <Select
              label="Project"
              data={projects.map((p) => ({
                value: p.id.toString(),
                label: p.name,
              }))}
              value={importProject}
              onChange={setImportProject}
              required
            />
            <Select
              label="Tool"
              data={[
                { value: "burp", label: "Burp Suite XML" },
                { value: "nessus", label: "Nessus XML" },
              ]}
              value={importTool}
              onChange={setImportTool}
              required
            />
            <FileInput
              label="Scan Report File"
              value={importFile}
              onChange={setImportFile}
              required
            />
            <Button
              disabled={!importFile || !importTool || !importProject}
              onClick={handleImport}
              loading={importLoading}
            >
              Import
            </Button>
            {importResult && (
              <Notification color={importResult.startsWith("Error") ? "red" : "green"}>
                {importResult}
              </Notification>
            )}
          </Stack>
        </Tabs.Panel>

        <Tabs.Panel value="export" pt="xl">
          <Stack>
            <Title order={4}>Export Project Report</Title>
            <Select
              label="Project"
              data={projects.map((p) => ({
                value: p.id.toString(),
                label: p.name,
              }))}
              value={exportProject}
              onChange={setExportProject}
              required
            />
            <Select
              label="Report Template"
              data={templates.map((t) => ({
                value: t.id.toString(),
                label: `${t.name} (${t.type})`,
              }))}
              value={exportTemplate}
              onChange={setExportTemplate}
              required
            />
            <Button
              disabled={!exportProject || !exportTemplate}
              onClick={handleExport}
              loading={exportLoading}
            >
              Export & Download
            </Button>
            {/* Optionally show manual download link */}
            {exportUrl && (
              <a href={exportUrl} download>
                Download Report
              </a>
            )}
          </Stack>
        </Tabs.Panel>
      </Tabs>
      <LoadingOverlay visible={importLoading || exportLoading} />
    </div>
  );
}