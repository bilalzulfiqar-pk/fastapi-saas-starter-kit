"use client";

import { createContext, ReactNode, useContext, useState } from "react";

type SidebarContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
};

const SidebarContext = createContext<SidebarContextValue | null>(null);

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(true);
  return <SidebarContext.Provider value={{ open, setOpen }}>{children}</SidebarContext.Provider>;
}

export function useSidebarState() {
  const value = useContext(SidebarContext);
  if (!value) {
    throw new Error("useSidebarState must be used within SidebarProvider");
  }
  return value;
}

