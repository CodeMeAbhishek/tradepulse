import { PrototypeBanner } from "@/components/PrototypeBanner";
import { AppNav } from "@/components/AppShell";

export function WorkbenchShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <PrototypeBanner />
      <AppNav />
      <div className="flex-1">{children}</div>
    </div>
  );
}
