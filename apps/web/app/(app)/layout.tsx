import { ReactNode } from "react";

import { AppShell } from "@/components/layout/app-shell";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}

