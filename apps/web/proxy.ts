import { NextRequest, NextResponse } from "next/server";

import { normalizeNextPath } from "@/lib/auth-navigation";
import { ACCESS_COOKIE_NAME, SESSION_COOKIE_NAME } from "@/lib/constants";

const protectedPrefixes = ["/dashboard", "/onboarding"];

export function proxy(request: NextRequest) {
  const { pathname, search, searchParams } = request.nextUrl;
  const hasAccessCookie = request.cookies.has(ACCESS_COOKIE_NAME);
  const hasSessionMarker = request.cookies.has(SESSION_COOKIE_NAME);
  const isProtected = protectedPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  const isAuthPage = pathname === "/login" || pathname === "/register";

  if (!hasAccessCookie && !hasSessionMarker && isProtected) {
    const redirectUrl = new URL(`/login?next=${encodeURIComponent(`${pathname}${search}`)}`, request.url);
    return NextResponse.redirect(redirectUrl);
  }

  if (hasAccessCookie && isAuthPage) {
    const inviteToken = searchParams.get("invite");
    if (inviteToken) {
      return NextResponse.redirect(new URL(`/dashboard?invite=${encodeURIComponent(inviteToken)}`, request.url));
    }
    const nextPath = normalizeNextPath(searchParams.get("next"));
    if (nextPath) {
      return NextResponse.redirect(new URL(nextPath, request.url));
    }
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/onboarding", "/login", "/register"],
};
