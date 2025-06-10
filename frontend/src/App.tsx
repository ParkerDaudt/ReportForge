import React from 'react';
import { MantineProvider, ColorSchemeProvider } from '@mantine/core';

function App() {
  const [colorScheme, setColorScheme] = React.useState<'light' | 'dark'>('dark');
  const toggleColorScheme = () =>
    setColorScheme((current) => (current === 'dark' ? 'light' : 'dark'));

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
      <MantineProvider theme={{ colorScheme }} withGlobalStyles withNormalizeCSS>
        {/* TODO: Add routing and pages */}
        <div style={{ padding: 40 }}>
          <h1>Pentest Reporting Tool</h1>
          <button onClick={toggleColorScheme}>Toggle dark mode</button>
        </div>
      </MantineProvider>
    </ColorSchemeProvider>
  );
}

export default App;