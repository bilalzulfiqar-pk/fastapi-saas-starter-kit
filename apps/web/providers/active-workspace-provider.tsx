"use client";

import { createContext, ReactNode, useContext, useMemo, useState } from "react";

export type WorkspaceOption = {
  id: string;
  name: string;
  slug: string;
  role: string;
};

type ActiveWorkspaceContextValue = {
  workspaceId: string | null;
  setWorkspaceId: (workspaceId: string | null) => void;
  syncWithWorkspaces: (workspaces: WorkspaceOption[]) => void;
};

const STORAGE_KEY = "starter.activeWorkspaceId";
const ActiveWorkspaceContext = createContext<ActiveWorkspaceContextValue | null>(null);

export function ActiveWorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspaceId, setWorkspaceId] = useState<string | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }
    return window.localStorage.getItem(STORAGE_KEY);
  });

  const value = useMemo(
    () => ({
      workspaceId,
      setWorkspaceId: (nextValue: string | null) => {
        setWorkspaceId(nextValue);
        if (nextValue) {
          window.localStorage.setItem(STORAGE_KEY, nextValue);
        } else {
          window.localStorage.removeItem(STORAGE_KEY);
        }
      },
      syncWithWorkspaces: (workspaces: WorkspaceOption[]) => {
        if (workspaces.length === 0) {
          setWorkspaceId(null);
          window.localStorage.removeItem(STORAGE_KEY);
          return;
        }
        const current = workspaceId;
        const stillExists = current ? workspaces.some((workspace) => workspace.id === current) : false;
        if (!stillExists) {
          const nextId = workspaces[0].id;
          setWorkspaceId(nextId);
          window.localStorage.setItem(STORAGE_KEY, nextId);
        }
      },
    }),
    [workspaceId],
  );

  return <ActiveWorkspaceContext.Provider value={value}>{children}</ActiveWorkspaceContext.Provider>;
}

export function useActiveWorkspace() {
  const value = useContext(ActiveWorkspaceContext);
  if (!value) {
    throw new Error("useActiveWorkspace must be used within ActiveWorkspaceProvider");
  }
  return value;
}
