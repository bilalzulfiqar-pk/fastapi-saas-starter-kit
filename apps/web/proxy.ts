import { NextRequest, NextResponse } from "next/server";

import { ACCESS_COOKIE_NAME } from "@/lib/constants";

const protectedPrefixes = ["/dashboard", "/onboarding"];

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasAccessCookie = request.cookies.has(ACCESS_COOKIE_NAME);
  const isProtected = protectedPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  const isAuthPage = pathname === "/login" || pathname === "/register";

  if (!hasAccessCookie && isProtected) {
    const redirectUrl = new URL(`/login?next=${encodeURIComponent(`${pathname}${search}`)}`, request.url);
    return NextResponse.redirect(redirectUrl);
  }

  if (hasAccessCookie && isAuthPage) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/onboarding", "/login", "/register"],
};

