import React from "react";
import { Navbar, NavLink, Stack } from "@mantine/core";
import { IconFolder, IconBug, IconTag, IconFileText, IconTemplate, IconSettings } from "@tabler/icons-react";
import { Link, useLocation } from "react-router-dom";

const navItems = [
  { label: "Projects", icon: IconFolder, to: "/" },
  { label: "Findings", icon: IconBug, to: "/findings" },
  { label: "Master Findings", icon: IconBug, to: "/master-findings" },
  { label: "Tags", icon: IconTag, to: "/tags" },
  { label: "Attachments", icon: IconFileText, to: "/attachments" },
  { label: "Templates", icon: IconTemplate, to: "/templates" },
  { label: "Import/Export", icon: IconUpload, to: "/import-export" },
  { label: "Settings", icon: IconSettings, to: "/settings" },
];

export function Sidebar() {
  const location = useLocation();
  return (
    <Navbar width={{ base: 200 }} p="xs">
      <Stack>
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            component={Link}
            to={item.to}
            label={item.label}
            icon={<item.icon size={18} />}
            active={location.pathname === item.to}
          />
        ))}
      </Stack>
    </Navbar>
  );
}