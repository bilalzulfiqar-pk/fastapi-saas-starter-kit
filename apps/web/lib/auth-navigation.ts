export function normalizeNextPath(nextUrl: string | null | undefined): string | null {
  if (!nextUrl || !nextUrl.startsWith("/") || nextUrl.startsWith("//")) {
    return null;
  }

  try {
    const url = new URL(nextUrl, "http://starter.local");
    const normalized = `${url.pathname}${url.search}${url.hash}`;
    if (normalized === "/login" || normalized.startsWith("/login?")) {
      return null;
    }
    if (normalized === "/register" || normalized.startsWith("/register?")) {
      return null;
    }
    return normalized;
  } catch {
    return null;
  }
}

export function buildAuthHref(
  pathname: "/login" | "/register",
  options: { inviteToken?: string | null; nextUrl?: string | null } = {},
): string {
  const params = new URLSearchParams();
  if (options.inviteToken) {
    params.set("invite", options.inviteToken);
  }
  const nextPath = normalizeNextPath(options.nextUrl);
  if (nextPath) {
    params.set("next", nextPath);
  }
  const search = params.toString();
  return search ? `${pathname}?${search}` : pathname;
}

export function getPostAuthDestination(options: {
  inviteToken?: string | null;
  nextUrl?: string | null;
  defaultPath: string;
}): string {
  if (options.inviteToken) {
    return `/dashboard?invite=${encodeURIComponent(options.inviteToken)}`;
  }

  return normalizeNextPath(options.nextUrl) ?? options.defaultPath;
}
