import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function MarketingHome() {
  return (
    <div className="page-shell">
      <section className="hero">
        <div className="stack">
          <p className="muted">Reusable SaaS foundation</p>
          <h1>Launch the boring parts once, then build the product that matters.</h1>
          <p className="muted">
            This starter gives you auth, workspaces, members, invites, billing-ready models, a dashboard shell, and docs without baking in any product-specific module.
          </p>
          <div className="inline-form">
            <Link href="/register">
              <Button type="button">Start with the starter</Button>
            </Link>
            <Link href="/login">
              <button className="ghost-button" type="button">Sign in</button>
            </Link>
          </div>
        </div>
        <Card>
          <div className="stack">
            <h2>What ships in v1</h2>
            <div className="list-row"><span>Auth</span><strong>Cookie-first</strong></div>
            <div className="list-row"><span>Workspaces</span><strong>Multi-tenant ready</strong></div>
            <div className="list-row"><span>Invites</span><strong>Console email adapter</strong></div>
            <div className="list-row"><span>Billing</span><strong>Models only</strong></div>
            <div className="list-row"><span>Frontend state</span><strong>TanStack Query + Context</strong></div>
          </div>
        </Card>
      </section>
    </div>
  );
}

