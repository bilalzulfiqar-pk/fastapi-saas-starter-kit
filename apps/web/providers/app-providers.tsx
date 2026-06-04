"use client";

import { ReactNode } from "react";

import { ActiveWorkspaceProvider } from "@/providers/active-workspace-provider";
import { QueryProvider } from "@/providers/query-provider";
import { SidebarProvider } from "@/providers/sidebar-provider";
import { ThemeProvider } from "@/providers/theme-provider";

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryProvider>
      <ThemeProvider>
        <SidebarProvider>
          <ActiveWorkspaceProvider>{children}</ActiveWorkspaceProvider>
        </SidebarProvider>
      </ThemeProvider>
    </QueryProvider>
  );
}

