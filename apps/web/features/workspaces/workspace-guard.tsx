"use client";

import { useEffect, useMemo, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";

import { Card } from "@/components/ui/card";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useWorkspaces } from "@/hooks/use-workspaces";

export function WorkspaceGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { workspaceId, syncWithWorkspaces } = useActiveWorkspace();
  const workspaces = useWorkspaces();
  const items = useMemo(() => workspaces.data?.data.workspaces ?? [], [workspaces.data]);
  const isOnboardingRoute = pathname === "/onboarding";
  const hasWorkspaces = items.length > 0;
  const hasActiveWorkspace = workspaceId ? items.some((workspace) => workspace.id === workspaceId) : false;

  useEffect(() => {
    if (!workspaces.data) {
      return;
    }
    syncWithWorkspaces(items);
  }, [items, syncWithWorkspaces, workspaces.data]);

  useEffect(() => {
    if (!workspaces.data) {
      return;
    }

    if (!hasWorkspaces && !isOnboardingRoute) {
      router.replace("/onboarding");
      return;
    }

    if (hasWorkspaces && isOnboardingRoute) {
      router.replace("/dashboard");
    }
  }, [hasWorkspaces, isOnboardingRoute, router, workspaces.data]);

  if (workspaces.isPending) {
    return (
      <Card>
        <h1>Loading workspaces</h1>
        <p className="muted">We are preparing your workspace context.</p>
      </Card>
    );
  }

  if (workspaces.error) {
    return (
      <Card>
        <h1>Unable to load workspaces</h1>
        <p className="error">{workspaces.error.message}</p>
      </Card>
    );
  }

  if (!hasWorkspaces && !isOnboardingRoute) {
    return (
      <Card>
        <h1>Redirecting to onboarding</h1>
        <p className="muted">You need a workspace before using the dashboard.</p>
      </Card>
    );
  }

  if (hasWorkspaces && isOnboardingRoute) {
    return (
      <Card>
        <h1>Workspace ready</h1>
        <p className="muted">Redirecting you back to the dashboard.</p>
      </Card>
    );
  }

  if (hasWorkspaces && !hasActiveWorkspace) {
    return (
      <Card>
        <h1>Preparing active workspace</h1>
        <p className="muted">We are syncing your preferred workspace.</p>
      </Card>
    );
  }

  return <>{children}</>;
}
