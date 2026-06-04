"use client";

import { Card } from "@/components/ui/card";
import { InvitePanel } from "@/features/invites/invite-panel";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useWorkspaceMembers } from "@/hooks/use-workspace-members";

export default function MembersSettingsPage() {
  const { workspaceId } = useActiveWorkspace();
  const members = useWorkspaceMembers(workspaceId);

  return (
    <div className="grid">
      <Card>
        <h1>Members</h1>
        <div className="stack stack--tight">
          {(members.data?.data.members ?? []).map((member) => (
            <div className="list-row" key={String(member.id)}>
              <span>{String(member.name)} ({String(member.email)})</span>
              <strong>{String(member.role)}</strong>
            </div>
          ))}
        </div>
      </Card>
      <InvitePanel workspaceId={workspaceId} />
    </div>
  );
}

