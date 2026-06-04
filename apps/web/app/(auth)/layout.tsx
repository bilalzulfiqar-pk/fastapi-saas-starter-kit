import { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return <div className="page-shell"><div className="auth-grid">{children}</div></div>;
}

