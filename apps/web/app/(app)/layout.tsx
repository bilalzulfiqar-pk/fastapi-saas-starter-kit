import { ReactNode } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { AuthGuard } from "@/features/auth/auth-guard";
import { WorkspaceGuard } from "@/features/workspaces/workspace-guard";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <AppShell>
        <WorkspaceGuard>{children}</WorkspaceGuard>
      </AppShell>
    </AuthGuard>
  );
}
