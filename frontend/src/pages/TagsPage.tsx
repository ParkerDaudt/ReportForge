import React, { useEffect, useState } from "react";
import api from "../api";
import {
  Table,
  Button,
  Group,
  Modal,
  TextInput,
  ActionIcon,
  Title,
  LoadingOverlay,
  Stack,
  Notification,
  Text,
} from "@mantine/core";
import { IconEdit, IconTrash, IconPlus } from "@tabler/icons-react";

type Tag = {
  id: number;
  name: string;
};

export function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTag, setEditTag] = useState<Tag | null>(null);
  const [form, setForm] = useState({ name: "" });
  const [search, setSearch] = useState("");
  const [notification, setNotification] = useState<{ color: string; msg: string } | null>(null);

  const fetchTags = async () => {
    setLoading(true);
    const res = await api.get("/tags/");
    setTags(res.data);
    setLoading(false);
  };

  useEffect(() => {
    fetchTags();
  }, []);

  const openCreate = () => {
    setEditTag(null);
    setForm({ name: "" });
    setModalOpen(true);
  };

  const openEdit = (tag: Tag) => {
    setEditTag(tag);
    setForm({ name: tag.name });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editTag) {
        await api.put(`/tags/${editTag.id}`, form);
        setNotification({ color: "blue", msg: "Tag updated!" });
      } else {
        await api.post("/tags/", form);
        setNotification({ color: "green", msg: "Tag created!" });
      }
      setModalOpen(false);
      fetchTags();
    } catch (e: any) {
      setNotification({ color: "red", msg: "Tag operation failed." });
    }
  };

  const handleDelete = async (tag: Tag) => {
    if (window.confirm(`Delete tag "${tag.name}"?`)) {
      try {
        await api.delete(`/tags/${tag.id}`);
        setNotification({ color: "orange", msg: "Tag deleted." });
        fetchTags();
      } catch {
        setNotification({ color: "red", msg: "Failed to delete tag." });
      }
    }
  };

  const filtered = !search
    ? tags
    : tags.filter((t) => t.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div style={{ position: "relative" }}>
      <LoadingOverlay visible={loading} />
      <Group position="apart" align="center" mb="md">
        <Title order={2}>Tags</Title>
        <Button leftIcon={<IconPlus size={16} />} onClick={openCreate}>
          Add Tag
        </Button>
      </Group>
      <TextInput
        label="Search"
        placeholder="Type to filter tags"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        mb="sm"
        style={{ maxWidth: 300 }}
      />
      <Table highlightOnHover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length > 0 ? (
            filtered.map((t) => (
              <tr key={t.id}>
                <td>{t.name}</td>
                <td>
                  <Group spacing={4}>
                    <ActionIcon onClick={() => openEdit(t)}>
                      <IconEdit size={16} />
                    </ActionIcon>
                    <ActionIcon color="red" onClick={() => handleDelete(t)}>
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={2}>
                <Text color="dimmed">No tags found.</Text>
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editTag ? "Edit Tag" : "Add Tag"}
      >
        <Stack>
          <TextInput
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <Button onClick={handleSubmit}>{editTag ? "Update" : "Create"}</Button>
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