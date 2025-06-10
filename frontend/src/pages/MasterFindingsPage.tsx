import React, { useEffect, useState } from "react";
import api from "../api";
import {
  Table,
  Button,
  Group,
  Modal,
  TextInput,
  Textarea,
  MultiSelect,
  ActionIcon,
  Title,
  LoadingOverlay,
  Select,
  Stack,
} from "@mantine/core";
import { IconEdit, IconTrash, IconCopy } from "@tabler/icons-react";

type MasterFinding = {
  id: number;
  title: string;
  technical_analysis: string;
  impact: string;
  frameworks: string[];
  recommendations: string;
  references: string;
  created_at: string;
  updated_at: string;
};

type Project = {
  id: number;
  name: string;
};

export function MasterFindingsPage() {
  const [masterFindings, setMasterFindings] = useState<MasterFinding[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editFinding, setEditFinding] = useState<MasterFinding | null>(null);
  const [form, setForm] = useState<Omit<MasterFinding, "id" | "created_at" | "updated_at">>({
    title: "",
    technical_analysis: "",
    impact: "",
    frameworks: [],
    recommendations: "",
    references: "",
  });

  // Clone to Project
  const [cloneModalOpen, setCloneModalOpen] = useState(false);
  const [cloneFinding, setCloneFinding] = useState<MasterFinding | null>(null);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);

  const fetchMasterFindings = async () => {
    setLoading(true);
    const res = await api.get("/master-findings/");
    setMasterFindings(res.data);
    setLoading(false);
  };
  const fetchProjects = async () => {
    const res = await api.get("/projects/");
    setProjects(res.data);
  };

  useEffect(() => {
    fetchMasterFindings();
    fetchProjects();
  }, []);

  const openCreate = () => {
    setEditFinding(null);
    setForm({
      title: "",
      technical_analysis: "",
      impact: "",
      frameworks: [],
      recommendations: "",
      references: "",
    });
    setModalOpen(true);
  };

  const openEdit = (finding: MasterFinding) => {
    setEditFinding(finding);
    setForm({
      title: finding.title,
      technical_analysis: finding.technical_analysis,
      impact: finding.impact,
      frameworks: finding.frameworks,
      recommendations: finding.recommendations,
      references: finding.references,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    if (editFinding) {
      await api.put(`/master-findings/${editFinding.id}`, form);
    } else {
      await api.post("/master-findings/", form);
    }
    setModalOpen(false);
    fetchMasterFindings();
  };

  const handleDelete = async (finding: MasterFinding) => {
    if (window.confirm(`Delete master finding "${finding.title}"?`)) {
      await api.delete(`/master-findings/${finding.id}`);
      fetchMasterFindings();
    }
  };

  // Clone to Project workflow
  const openClone = (finding: MasterFinding) => {
    setCloneFinding(finding);
    setSelectedProject(null);
    setCloneModalOpen(true);
  };

  const handleClone = async () => {
    if (!cloneFinding || !selectedProject) return;
    // Map master finding fields to project finding fields
    const findingPayload = {
      project_id: Number(selectedProject),
      name: cloneFinding.title,
      severity: "Info",
      description: cloneFinding.technical_analysis,
      cve: "",
      cwe: "",
      cvss: null,
      affected_host: "",
      status: "draft",
      recommendation: cloneFinding.recommendations,
      evidence: "",
      references: cloneFinding.references,
      notes: "",
      category: "",
      tag_ids: [],
    };
    await api.post("/findings/", findingPayload);
    setCloneModalOpen(false);
  };

  return (
    <div style={{ position: "relative" }}>
      <LoadingOverlay visible={loading} />
      <Group position="apart" align="center" mb="md">
        <Title order={2}>Master Findings</Title>
        <Button onClick={openCreate}>Add Master Finding</Button>
      </Group>
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
          {masterFindings.map((f) => (
            <tr key={f.id}>
              <td>{f.title}</td>
              <td>{f.frameworks.join(", ")}</td>
              <td>{f.impact}</td>
              <td>
                <Group spacing={4}>
                  <ActionIcon onClick={() => openEdit(f)}>
                    <IconEdit size={16} />
                  </ActionIcon>
                  <ActionIcon color="red" onClick={() => handleDelete(f)}>
                    <IconTrash size={16} />
                  </ActionIcon>
                  <ActionIcon color="blue" onClick={() => openClone(f)} title="Clone to Project">
                    <IconCopy size={16} />
                  </ActionIcon>
                </Group>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      {/* Create/Edit Modal */}
      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editFinding ? "Edit Master Finding" : "Add Master Finding"}
        size="lg"
      >
        <Stack>
          <TextInput
            label="Title"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            required
          />
          <Textarea
            label="Technical Analysis"
            value={form.technical_analysis}
            onChange={(e) => setForm((f) => ({ ...f, technical_analysis: e.target.value }))}
            minRows={3}
          />
          <Textarea
            label="Impact"
            value={form.impact}
            onChange={(e) => setForm((f) => ({ ...f, impact: e.target.value }))}
            minRows={2}
          />
          <MultiSelect
            label="Frameworks (NIST, MITRE, etc.)"
            data={[
              { value: "NIST-AC-1", label: "NIST-AC-1" },
              { value: "MITRE-T1003", label: "MITRE-T1003" },
              // Add more as needed or make this dynamic in future!
            ]}
            value={form.frameworks}
            searchable
            creatable
            getCreateLabel={(query) => `+ Add "${query}"`}
            onChange={(vals) => setForm((f) => ({ ...f, frameworks: vals }))}
          />
          <Textarea
            label="Recommendations"
            value={form.recommendations}
            onChange={(e) => setForm((f) => ({ ...f, recommendations: e.target.value }))}
            minRows={2}
          />
          <Textarea
            label="References"
            value={form.references}
            onChange={(e) => setForm((f) => ({ ...f, references: e.target.value }))}
            minRows={2}
          />
          <Button onClick={handleSubmit}>{editFinding ? "Update" : "Create"}</Button>
        </Stack>
      </Modal>
      {/* Clone to Project Modal */}
      <Modal
        opened={cloneModalOpen}
        onClose={() => setCloneModalOpen(false)}
        title="Clone Master Finding to Project"
      >
        <Stack>
          <Select
            label="Select Project"
            data={projects.map((p) => ({
              value: p.id.toString(),
              label: p.name,
            }))}
            value={selectedProject}
            onChange={setSelectedProject}
            required
          />
          <Button disabled={!selectedProject} onClick={handleClone}>
            Clone
          </Button>
        </Stack>
      </Modal>
    </div>
  );
}