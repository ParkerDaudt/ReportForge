import React, { useEffect, useState } from "react";
import api from "../api";
import {
  Table,
  Button,
  Group,
  Modal,
  TextInput,
  Textarea,
  Select,
  MultiSelect,
  ActionIcon,
  Title,
  LoadingOverlay,
  Stack,
} from "@mantine/core";
import { IconEdit, IconTrash, IconPlus, IconCopy } from "@tabler/icons-react";

type Finding = {
  id: number;
  name: string;
  severity: string;
  description: string;
  cve?: string;
  cwe?: string;
  cvss?: number;
  affected_host?: string;
  status: string;
  recommendation?: string;
  evidence?: string;
  references?: string;
  notes?: string;
  category?: string;
  tag_ids?: number[];
  tags?: { id: number; name: string }[];
  project_id: number;
};

type Project = {
  id: number;
  name: string;
};

type Tag = {
  id: number;
  name: string;
};

type MasterFinding = {
  id: number;
  title: string;
  technical_analysis: string;
  impact: string;
  frameworks: string[];
  recommendations: string;
  references: string;
};

const severityOptions = [
  { value: "Critical", label: "Critical" },
  { value: "High", label: "High" },
  { value: "Medium", label: "Medium" },
  { value: "Low", label: "Low" },
  { value: "Info", label: "Info" },
];

const statusOptions = [
  { value: "draft", label: "Draft" },
  { value: "confirmed", label: "Confirmed" },
  { value: "reported", label: "Reported" },
  { value: "false positive", label: "False Positive" },
  { value: "remediated", label: "Remediated" },
];

export function FindingsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editFinding, setEditFinding] = useState<Finding | null>(null);
  const [form, setForm] = useState<Omit<Finding, "id" | "tags" | "project_id">>({
    name: "",
    severity: "Info",
    description: "",
    cve: "",
    cwe: "",
    cvss: undefined,
    affected_host: "",
    status: "draft",
    recommendation: "",
    evidence: "",
    references: "",
    notes: "",
    category: "",
    tag_ids: [],
  });

  // Import from Master
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [masterFindings, setMasterFindings] = useState<MasterFinding[]>([]);

  const fetchProjects = async () => {
    const res = await api.get("/projects/");
    setProjects(res.data);
    if (res.data.length > 0 && !selectedProject) setSelectedProject(res.data[0].id.toString());
  };
  const fetchTags = async () => {
    const res = await api.get("/tags/");
    setTags(res.data);
  };
  const fetchFindings = async (projectId: string | null) => {
    if (!projectId) return;
    setLoading(true);
    const res = await api.get(`/projects/${projectId}/findings`);
    setFindings(res.data);
    setLoading(false);
  };
  useEffect(() => {
    fetchProjects();
    fetchTags();
    // eslint-disable-next-line
  }, []);
  useEffect(() => {
    if (selectedProject) fetchFindings(selectedProject);
    // eslint-disable-next-line
  }, [selectedProject]);

  const openCreate = () => {
    setEditFinding(null);
    setForm({
      name: "",
      severity: "Info",
      description: "",
      cve: "",
      cwe: "",
      cvss: undefined,
      affected_host: "",
      status: "draft",
      recommendation: "",
      evidence: "",
      references: "",
      notes: "",
      category: "",
      tag_ids: [],
    });
    setModalOpen(true);
  };

  const openEdit = (finding: Finding) => {
    setEditFinding(finding);
    setForm({
      name: finding.name || "",
      severity: finding.severity || "Info",
      description: finding.description || "",
      cve: finding.cve || "",
      cwe: finding.cwe || "",
      cvss: finding.cvss,
      affected_host: finding.affected_host || "",
      status: finding.status || "draft",
      recommendation: finding.recommendation || "",
      evidence: finding.evidence || "",
      references: finding.references || "",
      notes: finding.notes || "",
      category: finding.category || "",
      tag_ids: finding.tags ? finding.tags.map((t) => t.id) : [],
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    if (!selectedProject) return;
    const payload = { ...form, project_id: Number(selectedProject) };
    if (editFinding) {
      await api.put(`/findings/${editFinding.id}`, payload);
    } else {
      await api.post("/findings/", payload);
    }
    setModalOpen(false);
    fetchFindings(selectedProject);
  };

  const handleDelete = async (finding: Finding) => {
    if (window.confirm(`Delete finding "${finding.name}"?`)) {
      await api.delete(`/findings/${finding.id}`);
      if (selectedProject) fetchFindings(selectedProject);
    }
  };

  // Import from Master workflow
  const openImportFromMaster = async () => {
    const res = await api.get("/master-findings/");
    setMasterFindings(res.data);
    setImportModalOpen(true);
  };
  const handleImportFromMaster = (mf: MasterFinding) => {
    setForm((f) => ({
      ...f,
      name: mf.title,
      description: mf.technical_analysis,
      recommendation: mf.recommendations,
      references: mf.references,
      notes: mf.impact,
      // (You can map more fields or let users edit as needed)
    }));
    setImportModalOpen(false);
  };

  return (
    <div style={{ position: "relative" }}>
      <LoadingOverlay visible={loading} />
      <Group position="apart" align="center" mb="md">
        <Title order={2}>Findings</Title>
        <Button leftIcon={<IconPlus size={16} />} onClick={openCreate} disabled={!selectedProject}>
          Add Finding
        </Button>
      </Group>
      <Group mb="md">
        <Select
          label="Project"
          data={projects.map((p) => ({ value: p.id.toString(), label: p.name }))}
          value={selectedProject}
          onChange={setSelectedProject}
          placeholder="Select Project"
          style={{ minWidth: 220 }}
        />
      </Group>
      <Table highlightOnHover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Host</th>
            <th>Tags</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <tr key={f.id}>
              <td>{f.name}</td>
              <td>{f.severity}</td>
              <td>{f.status}</td>
              <td>{f.affected_host}</td>
              <td>
                {f.tags && f.tags.map((t) => t.name).join(", ")}
              </td>
              <td>
                <Group spacing={4}>
                  <ActionIcon onClick={() => openEdit(f)}>
                    <IconEdit size={16} />
                  </ActionIcon>
                  <ActionIcon color="red" onClick={() => handleDelete(f)}>
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      {/* Create/Edit Finding Modal */}
      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editFinding ? "Edit Finding" : "Add Finding"}
        size="lg"
      >
        <Stack>
          <Group position="apart">
            <Title order={4}>{editFinding ? "Edit" : "Create"} Finding</Title>
            <Button size="xs" leftIcon={<IconCopy size={14} />} variant="subtle" onClick={openImportFromMaster}>
              Import from Master
            </Button>
          </Group>
          <TextInput
            label="Name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
          />
          <Select
            label="Severity"
            data={severityOptions}
            value={form.severity}
            onChange={(val) => setForm((f) => ({ ...f, severity: val || "Info" }))}
            required
          />
          <Select
            label="Status"
            data={statusOptions}
            value={form.status}
            onChange={(val) => setForm((f) => ({ ...f, status: val || "draft" }))}
            required
          />
          <TextInput
            label="Affected Host"
            value={form.affected_host}
            onChange={(e) => setForm((f) => ({ ...f, affected_host: e.target.value }))}
          />
          <MultiSelect
            label="Tags"
            data={tags.map((t) => ({ value: t.id.toString(), label: t.name }))}
            value={form.tag_ids ? form.tag_ids.map(String) : []}
            onChange={(vals) => setForm((f) => ({ ...f, tag_ids: vals.map(Number) }))}
            searchable
          />
          <TextInput
            label="CVE"
            value={form.cve}
            onChange={(e) => setForm((f) => ({ ...f, cve: e.target.value }))}
          />
          <TextInput
            label="CWE"
            value={form.cwe}
            onChange={(e) => setForm((f) => ({ ...f, cwe: e.target.value }))}
          />
          <TextInput
            label="CVSS"
            type="number"
            value={form.cvss !== undefined && form.cvss !== null ? form.cvss : ""}
            onChange={(e) => setForm((f) => ({ ...f, cvss: e.target.value ? parseFloat(e.target.value) : undefined }))}
          />
          <TextInput
            label="Category"
            value={form.category}
            onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
          />
          <Textarea
            label="Description"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            minRows={2}
          />
          <Textarea
            label="Recommendation"
            value={form.recommendation}
            onChange={(e) => setForm((f) => ({ ...f, recommendation: e.target.value }))}
            minRows={2}
          />
          <Textarea
            label="Evidence"
            value={form.evidence}
            onChange={(e) => setForm((f) => ({ ...f, evidence: e.target.value }))}
            minRows={1}
          />
          <Textarea
            label="References"
            value={form.references}
            onChange={(e) => setForm((f) => ({ ...f, references: e.target.value }))}
            minRows={1}
          />
          <Textarea
            label="Notes"
            value={form.notes}
            onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
            minRows={1}
          />
          <Button onClick={handleSubmit}>{editFinding ? "Update" : "Create"}</Button>
        </Stack>
      </Modal>
      {/* Import from Master Modal */}
      <Modal
        opened={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        title="Import from Master Finding"
        size="lg"
      >
        <Table highlightOnHover>
          <thead>
            <tr>
              <th>Title</th>
              <th>Frameworks</th>
              <th>Impact</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {masterFindings.map((mf) => (
              <tr key={mf.id}>
                <td>{mf.title}</td>
                <td>{mf.frameworks.join(", ")}</td>
                <td style={{ maxWidth: 180 }}>{mf.impact}</td>
                <td>
                  <Button size="xs" variant="outline" onClick={() => handleImportFromMaster(mf)}>
                    Import
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Modal>
    </div>
  );
}