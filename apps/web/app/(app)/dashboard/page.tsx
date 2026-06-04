import { Suspense } from "react";

import { Card } from "@/components/ui/card";

import { DashboardClient } from "./dashboard-client";

function DashboardFallback() {
  return (
    <div className="grid">
      <Card>
        <h1>Dashboard</h1>
        <p className="muted">Loading your workspace shell...</p>
      </Card>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardFallback />}>
      <DashboardClient />
    </Suspense>
  );
}
