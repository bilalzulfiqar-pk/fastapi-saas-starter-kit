"use client";

import { ChangeEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { InvitePanel } from "@/features/invites/invite-panel";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useRemoveWorkspaceMember,
  useUpdateWorkspaceMemberRole,
  useWorkspaceMembers,
} from "@/hooks/use-workspace-members";
import { WorkspaceRole, useWorkspaces } from "@/hooks/use-workspaces";

export default function MembersSettingsPage() {
  const { workspaceId } = useActiveWorkspace();
  const currentUser = useCurrentUser();
  const workspaces = useWorkspaces();
  const members = useWorkspaceMembers(workspaceId);
  const updateRole = useUpdateWorkspaceMemberRole(workspaceId);
  const removeMember = useRemoveWorkspaceMember(workspaceId);
  const activeWorkspace = workspaces.data?.data.workspaces.find((workspace) => workspace.id === workspaceId);
  const canManageMembers = activeWorkspace?.role === "owner" || activeWorkspace?.role === "admin";
  const canManageOwnership = activeWorkspace?.role === "owner";
  const currentUserId = currentUser.data?.data.user.id;

  async function handleRoleChange(memberId: string, event: ChangeEvent<HTMLSelectElement>) {
    await updateRole.mutateAsync({ memberId, role: event.target.value as WorkspaceRole });
  }

  async function handleRemove(memberId: string, memberName: string) {
    if (!window.confirm(`Remove ${memberName} from this workspace?`)) {
      return;
    }
    await removeMember.mutateAsync(memberId);
  }

  return (
    <div className="grid">
      <Card>
        <h1>Members</h1>
        <p className="muted">Manage roles and access for the active workspace.</p>
        {!canManageMembers && activeWorkspace ? (
          <p className="muted">Only workspace owners and admins can change roles or remove members.</p>
        ) : null}
        {canManageMembers && !canManageOwnership ? (
          <p className="muted">Only workspace owners can grant, revoke, or remove owner roles.</p>
        ) : null}
        {updateRole.error ? <p className="error">{updateRole.error.message}</p> : null}
        {removeMember.error ? <p className="error">{removeMember.error.message}</p> : null}
        <div className="stack stack--tight">
          {members.isPending ? <p className="muted">Loading members...</p> : null}
          {!members.isPending && (members.data?.data.members ?? []).length === 0 ? (
            <p className="muted">No members found for this workspace yet.</p>
          ) : null}
          {(members.data?.data.members ?? []).map((member) => {
            const canManageThisMember = canManageMembers && (canManageOwnership || member.role !== "owner");
            return (
              <div className="list-row" key={String(member.id)}>
                <div>
                  <strong>{String(member.name)}</strong>
                  <p className="muted">
                    {String(member.email)}
                    {member.user_id === currentUserId ? " (You)" : ""}
                  </p>
                </div>
                <div className="list-row__actions">
                  {canManageThisMember ? (
                    <select
                      className="input input--compact"
                      disabled={updateRole.isPending || removeMember.isPending}
                      onChange={(event) => void handleRoleChange(member.id, event)}
                      value={member.role}
                    >
                      {canManageOwnership ? <option value="owner">Owner</option> : null}
                      <option value="admin">Admin</option>
                      <option value="member">Member</option>
                    </select>
                  ) : (
                    <strong>{member.role}</strong>
                  )}
                  <Button
                    disabled={!canManageThisMember || updateRole.isPending || removeMember.isPending}
                    onClick={() => void handleRemove(member.id, member.name)}
                    type="button"
                  >
                    {member.user_id === currentUserId ? "Leave" : "Remove"}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
      <InvitePanel workspaceId={workspaceId} />
    </div>
  );
}
