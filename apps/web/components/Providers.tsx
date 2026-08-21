"use client";

import { DemoProvider } from "@/lib/demo/DemoProvider";

export function Providers({ children }: { children: React.ReactNode }) {
  return <DemoProvider>{children}</DemoProvider>;
}
