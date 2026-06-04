import type { Metadata } from "next";
import { ReactNode } from "react";

import { AppProviders } from "@/providers/app-providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "FastAPI SaaS Starter Kit",
  description: "Reusable SaaS foundation built with Next.js and FastAPI.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}

