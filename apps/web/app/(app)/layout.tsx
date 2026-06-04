import { ReactNode, Suspense } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { AuthGuard } from "@/features/auth/auth-guard";
import { WorkspaceGuard } from "@/features/workspaces/workspace-guard";

function WorkspaceGuardFallback() {
  return (
    <Card>
      <h1>Preparing workspace</h1>
      <p className="muted">Loading your workspace access and invite context.</p>
    </Card>
  );
}

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <AppShell>
        <Suspense fallback={<WorkspaceGuardFallback />}>
          <WorkspaceGuard>{children}</WorkspaceGuard>
        </Suspense>
      </AppShell>
    </AuthGuard>
  );
}
