"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { InviteRecord, useCancelInvite, useCreateInvite, useWorkspaceInvites } from "@/hooks/use-workspace-invites";
import { WorkspaceRole, useWorkspaces } from "@/hooks/use-workspaces";

export function InvitePanel({ workspaceId }: { workspaceId: string | null }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<WorkspaceRole>("member");
  const workspaces = useWorkspaces();
  const invites = useWorkspaceInvites(workspaceId);
  const createInvite = useCreateInvite(workspaceId);
  const cancelInvite = useCancelInvite(workspaceId);
  const activeWorkspace = workspaces.data?.data.workspaces.find((workspace) => workspace.id === workspaceId);
  const canManageInvites = activeWorkspace?.role === "owner" || activeWorkspace?.role === "admin";
  const canInviteOwners = activeWorkspace?.role === "owner";

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!workspaceId) return;
    await createInvite.mutateAsync({ email, role });
    setEmail("");
    if (!canInviteOwners) {
      setRole("member");
    }
  }

  async function handleRevoke(invite: InviteRecord) {
    if (!window.confirm(`Revoke the invite for ${invite.email}?`)) {
      return;
    }
    await cancelInvite.mutateAsync(invite.id);
  }

  return (
    <Card>
      <h2>Invites</h2>
      <p className="muted">Create and revoke workspace invites without leaving settings.</p>
      {!canManageInvites && activeWorkspace ? (
        <p className="muted">Only workspace owners and admins can manage invites.</p>
      ) : null}
      {canManageInvites && !canInviteOwners ? (
        <p className="muted">Only workspace owners can send owner-role invites.</p>
      ) : null}
      <form className="inline-form" onSubmit={handleSubmit}>
        <Input onChange={(event) => setEmail(event.target.value)} placeholder="teammate@example.com" type="email" value={email} />
        <select
          className="input"
          disabled={!workspaceId || !canManageInvites || createInvite.isPending || cancelInvite.isPending}
          onChange={(event) => setRole(event.target.value as WorkspaceRole)}
          value={role}
        >
          <option value="member">Member</option>
          <option value="admin">Admin</option>
          {canInviteOwners ? <option value="owner">Owner</option> : null}
        </select>
        <Button disabled={!workspaceId || !canManageInvites || createInvite.isPending || cancelInvite.isPending} type="submit">
          Invite
        </Button>
      </form>
      {createInvite.data?.data.invite.invite_url ? <p className="success">Invite URL: {createInvite.data.data.invite.invite_url}</p> : null}
      {createInvite.error ? <p className="error">{createInvite.error.message}</p> : null}
      {cancelInvite.error ? <p className="error">{cancelInvite.error.message}</p> : null}
      <div className="stack stack--tight">
        {invites.isPending ? <p className="muted">Loading invites...</p> : null}
        {!invites.isPending && (invites.data?.data.invites ?? []).length === 0 ? (
          <p className="muted">No invites sent for this workspace yet.</p>
        ) : null}
        {(invites.data?.data.invites ?? []).map((invite) => {
          const canRevoke = canManageInvites && invite.status === "pending" && (canInviteOwners || invite.role !== "owner");
          return (
            <div className="list-row" key={invite.id}>
              <div>
                <strong>{invite.email}</strong>
                <p className="muted">
                  {invite.role} · {invite.status}
                </p>
              </div>
              <div className="list-row__actions">
                {invite.status === "pending" && canRevoke ? (
                  <Button
                    disabled={createInvite.isPending || cancelInvite.isPending}
                    onClick={() => void handleRevoke(invite)}
                    type="button"
                  >
                    Revoke
                  </Button>
                ) : (
                  <span className="muted">{invite.status}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
