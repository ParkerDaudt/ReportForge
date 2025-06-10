import React, { useEffect, useState } from "react";
import api from "../api";
import {
  Title,
  Group,
  Button,
  Table,
  Stack,
  Modal,
  Select,
  LoadingOverlay,
  Notification,
  FileInput,
  Text
} from "@mantine/core";
import { IconDownload, IconUpload, IconClock } from "@tabler/icons-react";

type AuditLog = {
  id: number;
  action: string;
  entity_type: string;
  entity_id: number;
  user?: string;
  timestamp: string;
  details?: string;
};

type Project = { id: number; name: string };
type Template = { id: number; name: string };

export function SettingsPage() {
  // Audit log
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);

  // Scheduling
  const [scheduleModal, setScheduleModal] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [frequency, setFrequency] = useState<string | null>("weekly");
  const [notification, setNotification] = useState<{ color: string; msg: string } | null>(null);

  // Backup/Restore
  const [backupLoading, setBackupLoading] = useState(false);
  const [restoreLoading, setRestoreLoading] = useState(false);
  const [restoreFile, setRestoreFile] = useState<File | null>(null);

  useEffect(() => {
    // Fetch audit logs (stub: replace with your backend call)
    api.get("/audit/") // You must implement this endpoint!
      .then((res) => setAuditLogs(res.data))
      .catch(() => setAuditLogs([]));
    api.get("/projects/").then((res) => setProjects(res.data));
    api.get("/report-templates/").then((res) => setTemplates(res.data));
  }, []);

  // Scheduling submission (stub)
  const handleSchedule = async () => {
    // Replace with actual backend call
    setScheduleModal(false);
    setNotification({ color: "green", msg: "Scheduled export!" });
  };

  // Backup/Restore handlers (stub)
  const handleBackup = async () => {
    setBackupLoading(true);
    window.open("/api/backup", "_blank"); // Adjust endpoint as implemented
    setTimeout(() => setBackupLoading(false), 2000);
  };

  const handleRestore = async () => {
    if (!restoreFile) return;
    setRestoreLoading(true);
    // Replace with actual backend call
    setTimeout(() => {
      setRestoreLoading(false);
      setNotification({ color: "green", msg: "Restore uploaded!" });
    }, 2000);
  };

  return (
    <div style={{ position: "relative" }}>
      <LoadingOverlay visible={loading || backupLoading || restoreLoading} />
      <Stack spacing="lg">
        <Group position="apart">
          <Title order={2}>Settings</Title>
        </Group>
        {/* Audit Log Viewer */}
        <div>
          <Title order={4}>Audit Log</Title>
          <Table highlightOnHover>
            <thead>
              <tr>
                <th>Time</th>
                <th>User</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={5}><Text color="dimmed">No audit log entries.</Text></td>
                </tr>
              ) : (
                auditLogs.map((l) => (
                  <tr key={l.id}>
                    <td>{new Date(l.timestamp).toLocaleString()}</td>
                    <td>{l.user || "—"}</td>
                    <td>{l.action}</td>
                    <td>{l.entity_type} #{l.entity_id}</td>
                    <td>{l.details}</td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </div>
        {/* Scheduling Recurring Reports */}
        <div>
          <Title order={4}>Schedule Recurring Report Export</Title>
          <Button leftIcon={<IconClock size={16} />} onClick={() => setScheduleModal(true)}>
            Schedule Export
          </Button>
        </div>
        {/* Backup/Restore */}
        <div>
          <Title order={4}>Backup / Restore</Title>
          <Group>
            <Button
              leftIcon={<IconDownload size={16} />}
              onClick={handleBackup}
              loading={backupLoading}
            >
              Download Backup
            </Button>
            <FileInput
              value={restoreFile}
              onChange={setRestoreFile}
              placeholder="Choose backup file"
            />
            <Button
              leftIcon={<IconUpload size={16} />}
              onClick={handleRestore}
              loading={restoreLoading}
              disabled={!restoreFile}
            >
              Restore Backup
            </Button>
          </Group>
        </div>
        {/* Notifications */}
        {notification && (
          <Notification
            color={notification.color as any}
            onClose={() => setNotification(null)}
            mt="md"
          >
            {notification.msg}
          </Notification>
        )}
        {/* Schedule Modal */}
        <Modal
          opened={scheduleModal}
          onClose={() => setScheduleModal(false)}
          title="Schedule Recurring Export"
        >
          <Stack>
            <Select
              label="Project"
              data={projects.map((p) => ({
                value: p.id.toString(),
                label: p.name,
              }))}
              value={selectedProject}
              onChange={setSelectedProject}
              required
            />
            <Select
              label="Report Template"
              data={templates.map((t) => ({
                value: t.id.toString(),
                label: t.name,
              }))}
              value={selectedTemplate}
              onChange={setSelectedTemplate}
              required
            />
            <Select
              label="Frequency"
              data={[
                { value: "daily", label: "Daily" },
                { value: "weekly", label: "Weekly" },
                { value: "monthly", label: "Monthly" },
              ]}
              value={frequency}
              onChange={setFrequency}
              required
            />
            <Button onClick={handleSchedule}>Schedule</Button>
          </Stack>
        </Modal>
      </Stack>
    </div>
  );
}