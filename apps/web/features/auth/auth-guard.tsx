"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { Card } from "@/components/ui/card";
import { useCurrentUser } from "@/hooks/use-current-user";
import { ApiError } from "@/lib/api-client";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const currentUser = useCurrentUser();

  useEffect(() => {
    if (!(currentUser.error instanceof ApiError) || currentUser.error.status !== 401) {
      return;
    }

    const nextPath = `${window.location.pathname}${window.location.search}`;
    router.replace(`/login?next=${encodeURIComponent(nextPath)}`);
  }, [currentUser.error, router]);

  if (currentUser.isPending) {
    return (
      <Card>
        <h1>Checking your session</h1>
        <p className="muted">We are validating your access and refreshing it when needed.</p>
      </Card>
    );
  }

  if (currentUser.error instanceof ApiError && currentUser.error.status === 401) {
    return (
      <Card>
        <h1>Redirecting to login</h1>
        <p className="muted">Your session could not be restored.</p>
      </Card>
    );
  }

  if (currentUser.error) {
    return (
      <Card>
        <h1>Unable to load your account</h1>
        <p className="error">{currentUser.error.message}</p>
      </Card>
    );
  }

  return <>{children}</>;
}
