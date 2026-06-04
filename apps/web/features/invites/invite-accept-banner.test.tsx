import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { InviteAcceptBanner } from "@/features/invites/invite-accept-banner";

const mocks = vi.hoisted(() => ({
  replace: vi.fn(),
  refresh: vi.fn(),
  inviteState: {
    isLoading: false,
    error: null,
    data: {
      data: {
        invite: {
          role: "member",
          email: "teammate@example.com",
        },
      },
    },
  } as {
    isLoading: boolean;
    error: Error | null;
    data: { data: { invite: { role: string; email: string } } } | null;
  },
  acceptState: {
    mutateAsync: vi.fn(),
    isPending: false,
    error: null,
  } as {
    mutateAsync: ReturnType<typeof vi.fn>;
    isPending: boolean;
    error: Error | null;
  },
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: mocks.replace,
    refresh: mocks.refresh,
  }),
}));

vi.mock("@/hooks/use-workspace-invites", () => ({
  useInvite: () => mocks.inviteState,
  useAcceptInvite: () => mocks.acceptState,
}));

describe("InviteAcceptBanner", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.inviteState.isLoading = false;
    mocks.inviteState.error = null;
    mocks.inviteState.data = {
      data: {
        invite: {
          role: "member",
          email: "teammate@example.com",
        },
      },
    };
    mocks.acceptState.mutateAsync = vi.fn().mockResolvedValue({ data: { invite: { id: "invite-1" } } });
    mocks.acceptState.isPending = false;
    mocks.acceptState.error = null;
  });

  it("accepts the invite and returns the user to the dashboard", async () => {
    render(<InviteAcceptBanner token="invite-token" />);

    expect(screen.getByText(/workspace invite/i)).toBeInTheDocument();
    expect(screen.getByText(/teammate@example.com/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /accept invite/i }));

    await waitFor(() => expect(mocks.acceptState.mutateAsync).toHaveBeenCalledWith("invite-token"));
    await waitFor(() => expect(mocks.replace).toHaveBeenCalledWith("/dashboard"));
    expect(mocks.refresh).toHaveBeenCalled();
  });

  it("renders the invite lookup error when the token is invalid", () => {
    mocks.inviteState.error = new Error("Invite has expired");
    mocks.inviteState.data = null;

    render(<InviteAcceptBanner token="expired-token" />);

    expect(screen.getByText("Invite has expired")).toBeInTheDocument();
  });
});
