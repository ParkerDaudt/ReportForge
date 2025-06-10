import React, { useEffect, useState } from "react";
import api from "../api";
import {
  Table,
  Button,
  Group,
  Modal,
  TextInput,
  Textarea,
  Stack,
  ActionIcon,
  Title,
  LoadingOverlay,
  Notification,
} from "@mantine/core";
import { IconEdit, IconTrash, IconSearch } from "@tabler/icons-react";

type Project = {
  id: number;
  name: string;
  client?: string;
  assessment_dates?: string;
  scope?: string;
  team_members?: string;
  metadata?: string;
};

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editProject, setEditProject] = useState<Project | null>(null);
  const [form, setForm] = useState<Omit<Project, "id">>({
    name: "",
    client: "",
    assessment_dates: "",
    scope: "",
    team_members: "",
    metadata: "",
  });
  const [search, setSearch] = useState("");
  const [notification, setNotification] = useState<{ color: string; msg: string } | null>(null);

  const fetchProjects = async () => {
    setLoading(true);
    const res = await api.get("/projects/");
    setProjects(res.data);
    setLoading(false);
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const openCreate = () => {
    setEditProject(null);
    setForm({
      name: "",
      client: "",
      assessment_dates: "",
      scope: "",
      team_members: "",
      metadata: "",
    });
    setModalOpen(true);
  };

  const openEdit = (project: Project) => {
    setEditProject(project);
    setForm({
      name: project.name,
      client: project.client || "",
      assessment_dates: project.assessment_dates || "",
      scope: project.scope || "",
      team_members: project.team_members || "",
      metadata: project.metadata || "",
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editProject) {
        await api.put(`/projects/${editProject.id}`, form);
        setNotification({ color: "blue", msg: "Project updated!" });
      } else {
        await api.post("/projects/", form);
        setNotification({ color: "green", msg: "Project created!" });
      }
      setModalOpen(false);
      fetchProjects();
    } catch {
      setNotification({ color: "red", msg: "Project operation failed." });
    }
  };

  const handleDelete = async (project: Project) => {
    if (window.confirm(`Delete project "${project.name}"?`)) {
      try {
        await api.delete(`/projects/${project.id}`);
        setNotification({ color: "orange", msg: "Project deleted." });
        fetchProjects();
      } catch {
        setNotification({ color: "red", msg: "Failed to delete project." });
      }
    }
  };

  const filtered = !search
    ? projects
    : projects.filter((p) =>
        (p.name || "").toLowerCase().includes(search.toLowerCase()) ||
        (p.client || "").toLowerCase().includes(search.toLowerCase())
      );

  return (
    <div style={{ position: "relative" }}>
      <LoadingOverlay visible={loading} />
      <Group position="apart" align="center" mb="md">
        <Title order={2}>Projects</Title>
        <Button onClick={openCreate}>Add Project</Button>
      </Group>
      <Group mb="sm">
        <TextInput
          icon={<IconSearch size={16} />}
          placeholder="Search by name or client"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: 300 }}
        />
      </Group>
      <Table highlightOnHover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Client</th>
            <th>Assessment Dates</th>
            <th>Team</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((p) => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{p.client}</td>
              <td>{p.assessment_dates}</td>
              <td>{p.team_members}</td>
              <td>
                <Group spacing={4}>
                  <ActionIcon onClick={() => openEdit(p)}>
                    <IconEdit size={16} />
                  </ActionIcon>
                  <ActionIcon color="red" onClick={() => handleDelete(p)}>
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editProject ? "Edit Project" : "Add Project"}
      >
        <Stack>
          <TextInput
            label="Name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
          />
          <TextInput
            label="Client"
            value={form.client}
            onChange={(e) => setForm((f) => ({ ...f, client: e.target.value }))}
          />
          <TextInput
            label="Assessment Dates"
            value={form.assessment_dates}
            onChange={(e) => setForm((f) => ({ ...f, assessment_dates: e.target.value }))}
          />
          <TextInput
            label="Team Members"
            value={form.team_members}
            onChange={(e) => setForm((f) => ({ ...f, team_members: e.target.value }))}
          />
          <Textarea
            label="Scope"
            value={form.scope}
            onChange={(e) => setForm((f) => ({ ...f, scope: e.target.value }))}
          />
          <Textarea
            label="Metadata"
            value={form.metadata}
            onChange={(e) => setForm((f) => ({ ...f, metadata: e.target.value }))}
          />
          <Button onClick={handleSubmit}>{editProject ? "Update" : "Create"}</Button>
        </Stack>
      </Modal>
      {notification && (
        <Notification
          color={notification.color as any}
          onClose={() => setNotification(null)}
          mt="md"
        >
          {notification.msg}
        </Notification>
      )}
    </div>
  );
}