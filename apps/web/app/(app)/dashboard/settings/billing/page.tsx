"use client";

import { SubscriptionCard } from "@/features/billing/subscription-card";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";

export default function BillingSettingsPage() {
  const { workspaceId } = useActiveWorkspace();
  return <SubscriptionCard workspaceId={workspaceId} />;
}

