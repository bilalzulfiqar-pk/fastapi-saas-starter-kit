import { act, renderHook } from "@testing-library/react";
import React, { ReactNode } from "react";

import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { ActiveWorkspaceProvider } from "@/providers/active-workspace-provider";

function wrapper({ children }: { children: ReactNode }) {
  return <ActiveWorkspaceProvider>{children}</ActiveWorkspaceProvider>;
}

describe("useActiveWorkspace", () => {
  it("exposes the active workspace setter", () => {
    const { result } = renderHook(() => useActiveWorkspace(), { wrapper });
    expect(result.current.workspaceId).toBeNull();
    act(() => {
      result.current.setWorkspaceId("workspace-1");
    });
    expect(result.current.workspaceId).toBe("workspace-1");
  });
});
