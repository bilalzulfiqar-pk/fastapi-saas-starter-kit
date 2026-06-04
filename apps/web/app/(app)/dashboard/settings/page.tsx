import Link from "next/link";

import { Card } from "@/components/ui/card";

export default function SettingsIndexPage() {
  return (
    <Card>
      <h1>Settings</h1>
      <p className="muted">Choose a settings area to continue.</p>
      <div className="stack">
        <Link href="/dashboard/settings/profile">Profile</Link>
        <Link href="/dashboard/settings/workspace">Workspace</Link>
        <Link href="/dashboard/settings/members">Members</Link>
        <Link href="/dashboard/settings/billing">Billing</Link>
        <Link href="/dashboard/settings/security">Security</Link>
      </div>
    </Card>
  );
}

