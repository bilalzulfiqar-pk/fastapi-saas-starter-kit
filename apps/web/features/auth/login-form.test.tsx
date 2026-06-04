import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "@/features/auth/login-form";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  refresh: vi.fn(),
  mutateAsync: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mocks.push,
    refresh: mocks.refresh,
  }),
}));

vi.mock("@/hooks/use-current-user", () => ({
  useLogin: () => ({
    mutateAsync: mocks.mutateAsync,
    isPending: false,
    error: null,
  }),
}));

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.mutateAsync.mockResolvedValue({ data: { user: { id: "user-1" } } });
  });

  it("preserves invite and next context across the auth surface", async () => {
    render(<LoginForm inviteToken="invite-token" nextUrl="/dashboard/settings/profile" />);

    const createAccountLink = screen.getByRole("link", { name: /create one/i });
    expect(createAccountLink).toHaveAttribute(
      "href",
      "/register?invite=invite-token&next=%2Fdashboard%2Fsettings%2Fprofile",
    );

    const email = screen.getByLabelText(/email/i);
    const password = screen.getByLabelText(/password/i);
    expect(email).toBeRequired();
    expect(password).toBeRequired();
    expect(password).toHaveAttribute("minlength", "8");

    fireEvent.change(email, { target: { value: "owner@example.com" } });
    fireEvent.change(password, { target: { value: "supersecret" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() =>
      expect(mocks.mutateAsync).toHaveBeenCalledWith({ email: "owner@example.com", password: "supersecret" }),
    );
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/dashboard?invite=invite-token"));
    expect(mocks.refresh).toHaveBeenCalled();
  });
});
