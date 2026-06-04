"use client";

import { FormEvent, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useUpdateWorkspace, useWorkspaces } from "@/hooks/use-workspaces";

export default function WorkspaceSettingsPage() {
  const { workspaceId } = useActiveWorkspace();
  const workspaces = useWorkspaces();
  const workspace = useMemo(
    () => workspaces.data?.data.workspaces.find((item) => item.id === workspaceId),
    [workspaceId, workspaces.data],
  );
  const [name, setName] = useState<string | null>(null);
  const draftName = name ?? workspace?.name ?? "";
  const mutation = useUpdateWorkspace(workspaceId);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await mutation.mutateAsync({ name: draftName });
  }

  return (
    <Card>
      <h1>Workspace</h1>
      <p className="muted">Rename and manage the currently active workspace foundation.</p>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Workspace name
          <Input onChange={(event) => setName(event.target.value)} value={draftName} />
        </label>
        {mutation.error ? <p className="error">{mutation.error.message}</p> : null}
        <Button disabled={!workspaceId || mutation.isPending} type="submit">
          Save workspace
        </Button>
      </form>
    </Card>
  );
}
