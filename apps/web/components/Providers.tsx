"use client";

import { DemoProvider } from "@/lib/demo/DemoProvider";
import { AppShell } from "@/components/shell/AppShell";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <DemoProvider>
      <AppShell>{children}</AppShell>
    </DemoProvider>
  );
}
