"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAcceptInvite, useInvite } from "@/hooks/use-workspace-invites";

export function InviteAcceptBanner({ token }: { token: string | null }) {
  const router = useRouter();
  const invite = useInvite(token);
  const accept = useAcceptInvite();

  if (!token || invite.isLoading) {
    return null;
  }
  if (invite.error) {
    return <Card><p className="error">{invite.error.message}</p></Card>;
  }
  if (!invite.data) {
    return null;
  }

  const inviteData = invite.data.data.invite as { email: string; role: string };

  return (
    <Card className="banner">
      <div>
        <strong>Workspace invite</strong>
        <p className="muted">
          You were invited as {inviteData.role} for {inviteData.email}.
        </p>
      </div>
      <Button
        onClick={async () => {
          await accept.mutateAsync(token);
          router.replace("/dashboard");
          router.refresh();
        }}
        type="button"
      >
        Accept invite
      </Button>
    </Card>
  );
}

