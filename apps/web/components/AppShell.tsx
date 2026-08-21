import type { ReactNode } from "react";
import { AppNav } from "@/components/AppNav";
import { PrototypeBanner } from "@/components/PrototypeBanner";
import styles from "./AppShell.module.css";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className={styles.shell}>
      <PrototypeBanner />
      <AppNav />
      <main className={styles.main}>{children}</main>
    </div>
  );
}
