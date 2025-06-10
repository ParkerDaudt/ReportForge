import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MantineProvider, ColorSchemeProvider, AppShell, Header, Group, Title, Button } from '@mantine/core';
import { Sidebar } from './components/Sidebar';
import { ProjectsPage } from './pages/ProjectsPage';
import { FindingsPage } from './pages/FindingsPage';
import { TagsPage } from './pages/TagsPage';
import { AttachmentsPage } from './pages/AttachmentsPage';
import { TemplatesPage } from './pages/TemplatesPage';
import { SettingsPage } from './pages/SettingsPage';

function App() {
  const [colorScheme, setColorScheme] = React.useState<'light' | 'dark'>('dark');
  const toggleColorScheme = () =>
    setColorScheme((current) => (current === 'dark' ? 'light' : 'dark'));

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
      <MantineProvider theme={{ colorScheme }} withGlobalStyles withNormalizeCSS>
        <BrowserRouter>
          <AppShell
            navbar={<Sidebar />}
            header={
              <Header height={60} p="xs">
                <Group position="apart">
                  <Title order={3}>Pentest Reporting Tool</Title>
                  <Button onClick={toggleColorScheme} size="xs" variant="default">
                    Toggle {colorScheme === "dark" ? "Light" : "Dark"} Mode
                  </Button>
                </Group>
              </Header>
            }
            padding="md"
          >
            <Routes>
              <Route path="/" element={<ProjectsPage />} />
              <Route path="/findings" element={<FindingsPage />} />
              <Route path="/tags" element={<TagsPage />} />
              <Route path="/attachments" element={<AttachmentsPage />} />
              <Route path="/templates" element={<TemplatesPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </AppShell>
        </BrowserRouter>
      </MantineProvider>
    </ColorSchemeProvider>
  );
}

export default App;