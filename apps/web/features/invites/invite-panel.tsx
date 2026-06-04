"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useCreateInvite, useWorkspaceInvites } from "@/hooks/use-workspace-invites";

export function InvitePanel({ workspaceId }: { workspaceId: string | null }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");
  const invites = useWorkspaceInvites(workspaceId);
  const createInvite = useCreateInvite(workspaceId);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!workspaceId) return;
    await createInvite.mutateAsync({ email, role });
    setEmail("");
  }

  return (
    <Card>
      <h2>Invites</h2>
      <form className="inline-form" onSubmit={handleSubmit}>
        <Input onChange={(event) => setEmail(event.target.value)} placeholder="teammate@example.com" type="email" value={email} />
        <select className="input" onChange={(event) => setRole(event.target.value)} value={role}>
          <option value="member">Member</option>
          <option value="admin">Admin</option>
          <option value="owner">Owner</option>
        </select>
        <Button disabled={!workspaceId || createInvite.isPending} type="submit">
          Invite
        </Button>
      </form>
      {createInvite.data ? <p className="success">Invite URL: {(createInvite.data as { data: { invite: { invite_url: string } } }).data.invite.invite_url}</p> : null}
      {createInvite.error ? <p className="error">{createInvite.error.message}</p> : null}
      <div className="stack stack--tight">
        {(invites.data?.data.invites ?? []).map((invite) => (
          <div className="list-row" key={String(invite.id)}>
            <span>{String(invite.email)}</span>
            <span className="muted">
              {String(invite.role)} · {String(invite.status)}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}

