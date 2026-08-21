import { AppShell } from "@/components/shell/AppShell";

export default function WorkbenchLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
