import { AppShell } from "@/components/shell/AppShell";

/** @deprecated Prefer AppShell via workbench layout; kept for any residual imports. */
export function WorkbenchShell({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
