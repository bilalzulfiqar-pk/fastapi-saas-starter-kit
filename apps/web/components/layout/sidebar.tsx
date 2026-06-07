"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { WorkspaceSwitcher } from "@/features/workspaces/workspace-switcher";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/settings/profile", label: "Profile" },
  { href: "/dashboard/settings/workspace", label: "Workspace" },
  { href: "/dashboard/settings/members", label: "Members" },
  { href: "/dashboard/settings/billing", label: "Billing" },
  { href: "/dashboard/settings/security", label: "Security" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">FastAPI SaaS Starter</div>
      <WorkspaceSwitcher />
      <nav className="sidebar__nav">
        {links.map((link) => (
          <Link key={link.href} className={cn("sidebar__link", pathname === link.href && "sidebar__link--active")} href={link.href}>
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
