import { describe, expect, it } from "vitest";

import { buildAuthHref, getPostAuthDestination, normalizeNextPath } from "@/lib/auth-navigation";

describe("auth navigation helpers", () => {
  it("accepts safe internal next paths and rejects external or auth-page redirects", () => {
    expect(normalizeNextPath("/dashboard/settings/profile?tab=security")).toBe("/dashboard/settings/profile?tab=security");
    expect(normalizeNextPath("https://evil.example")).toBeNull();
    expect(normalizeNextPath("//evil.example")).toBeNull();
    expect(normalizeNextPath("/login?next=%2Fdashboard")).toBeNull();
    expect(normalizeNextPath("/register")).toBeNull();
  });

  it("builds auth links that preserve invite and next context", () => {
    expect(buildAuthHref("/register", { inviteToken: "abc123", nextUrl: "/dashboard/settings" })).toBe(
      "/register?invite=abc123&next=%2Fdashboard%2Fsettings",
    );
    expect(buildAuthHref("/login", { nextUrl: "https://evil.example" })).toBe("/login");
  });

  it("chooses invite acceptance over generic next navigation after auth", () => {
    expect(
      getPostAuthDestination({
        inviteToken: "invite-token",
        nextUrl: "/dashboard/settings/workspace",
        defaultPath: "/dashboard",
      }),
    ).toBe("/dashboard?invite=invite-token");

    expect(
      getPostAuthDestination({
        nextUrl: "/dashboard/settings/workspace",
        defaultPath: "/onboarding",
      }),
    ).toBe("/dashboard/settings/workspace");
  });
});
