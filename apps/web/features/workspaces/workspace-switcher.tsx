"use client";

import { ChangeEvent, useMemo } from "react";

import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useWorkspaces } from "@/hooks/use-workspaces";

export function WorkspaceSwitcher() {
  const { workspaceId, setWorkspaceId } = useActiveWorkspace();
  const workspaces = useWorkspaces();
  const items = useMemo(() => workspaces.data?.data.workspaces ?? [], [workspaces.data]);

  if (items.length === 0) {
    return <p className="muted">No workspace yet</p>;
  }

  return (
    <label className="stack stack--tight">
      <span className="muted">Active workspace</span>
      <select
        className="input"
        onChange={(event: ChangeEvent<HTMLSelectElement>) => setWorkspaceId(event.target.value)}
        value={workspaceId ?? items[0]?.id}
      >
        {items.map((workspace) => (
          <option key={workspace.id} value={workspace.id}>
            {workspace.name} ({workspace.role})
          </option>
        ))}
      </select>
    </label>
  );
}
