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
  const ownerCount = (members.data?.data.members ?? []).filter((member) => member.role === "owner").length;

  async function handleRoleChange(memberId: string, event: ChangeEvent<HTMLSelectElement>) {
    await updateRole.mutateAsync({ memberId, role: event.target.value as WorkspaceRole });
  }

  async function handleRemove(memberId: string, memberName: string, isSelf: boolean) {
    const confirmationMessage = isSelf ? "Leave this workspace?" : `Remove ${memberName} from this workspace?`;
    if (!window.confirm(confirmationMessage)) {
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
          <p className="muted">Only workspace owners and admins can manage other members. You can still leave a workspace you belong to.</p>
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
            const isSelf = member.user_id === currentUserId;
            const canManageThisMember = canManageMembers && (canManageOwnership || member.role !== "owner");
            const canLeaveWorkspace = isSelf && (member.role !== "owner" || ownerCount > 1);
            const canShowRemoveAction = isSelf ? canLeaveWorkspace : canManageThisMember;
            return (
              <div className="list-row" key={String(member.id)}>
                <div>
                  <strong>{String(member.name)}</strong>
                  <p className="muted">
                    {String(member.email)}
                    {isSelf ? " (You)" : ""}
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
                  {canShowRemoveAction ? (
                    <Button
                      disabled={updateRole.isPending || removeMember.isPending}
                      onClick={() => void handleRemove(member.id, member.name, isSelf)}
                      type="button"
                    >
                      {isSelf ? "Leave" : "Remove"}
                    </Button>
                  ) : null}
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
