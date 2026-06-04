"use client";

import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api-client";
import { useSidebarState } from "@/providers/sidebar-provider";
import { useTheme } from "@/providers/theme-provider";

export function Topbar() {
  const router = useRouter();
  const { open, setOpen } = useSidebarState();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="topbar">
      <div className="topbar__left">
        <button className="ghost-button" onClick={() => setOpen(!open)} type="button">
          Menu
        </button>
      </div>
      <div className="topbar__right">
        <button className="ghost-button" onClick={toggleTheme} type="button">
          Theme: {theme}
        </button>
        <button
          className="ghost-button"
          onClick={async () => {
            await apiFetch("/api/v1/auth/logout", { method: "POST" });
            router.push("/login");
            router.refresh();
          }}
          type="button"
        >
          Logout
        </button>
      </div>
    </header>
  );
}

