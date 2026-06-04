"use client";

import { useSearchParams } from "next/navigation";

import { Card } from "@/components/ui/card";
import { InviteAcceptBanner } from "@/features/invites/invite-accept-banner";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useWorkspaces } from "@/hooks/use-workspaces";

export default function DashboardPage() {
  const params = useSearchParams();
  const { workspaceId } = useActiveWorkspace();
  const user = useCurrentUser();
  const workspaces = useWorkspaces();

  return (
    <div className="grid">
      <InviteAcceptBanner token={params.get("invite")} />
      <div className="grid grid--two">
        <Card>
          <h1>Dashboard</h1>
          <p className="muted">The starter shell is ready for your actual SaaS module.</p>
          <div className="stack stack--tight">
            <div className="list-row"><span>Signed in</span><strong>{user.data?.data.user.email ?? "Loading..."}</strong></div>
            <div className="list-row"><span>Active workspace</span><strong>{workspaceId ?? "None selected"}</strong></div>
            <div className="list-row"><span>Workspace count</span><strong>{String(workspaces.data?.data.workspaces.length ?? 0)}</strong></div>
          </div>
        </Card>
        <Card>
          <h2>How to extend this starter</h2>
          <p className="muted">Add product-specific backend and dashboard modules after this foundation is stable.</p>
        </Card>
      </div>
    </div>
  );
}

