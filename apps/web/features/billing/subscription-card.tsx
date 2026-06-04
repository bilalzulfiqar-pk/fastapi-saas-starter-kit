"use client";

import { Card } from "@/components/ui/card";
import { useBillingPlans, useWorkspaceSubscription } from "@/hooks/use-workspace-subscription";

export function SubscriptionCard({ workspaceId }: { workspaceId: string | null }) {
  const subscription = useWorkspaceSubscription(workspaceId);
  const plans = useBillingPlans();
  const planMap = new Map((plans.data?.data.plans ?? []).map((plan) => [String(plan.id), plan]));
  const current = subscription.data?.data.subscription;
  const plan = current ? planMap.get(String(current.plan_id)) : undefined;

  return (
    <Card>
      <h2>Billing-ready status</h2>
      <p className="muted">This MVP keeps billing read-only while preserving the core SaaS subscription models.</p>
      {current ? (
        <div className="stack stack--tight">
          <div className="list-row">
            <span>Status</span>
            <strong>{String(current.status)}</strong>
          </div>
          <div className="list-row">
            <span>Plan</span>
            <strong>{plan ? String(plan.name) : String(current.plan_id)}</strong>
          </div>
        </div>
      ) : (
        <p className="muted">No subscription loaded yet.</p>
      )}
    </Card>
  );
}

