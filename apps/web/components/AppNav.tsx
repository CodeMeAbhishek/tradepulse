"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./AppNav.module.css";

const LINKS = [
  { href: "/queue", label: "Queue" },
  { href: "/regwatch", label: "RegWatch", stub: true },
  { href: "/kpis", label: "KPIs", stub: true },
] as const;

export function AppNav() {
  const pathname = usePathname();

  return (
    <nav className={styles.nav} aria-label="Workbench">
      <div className={styles.brandBlock}>
        <span className={styles.brand}>TradePulse</span>
        <span className={styles.product}>Compliance workbench</span>
      </div>
      <ul className={styles.list}>
        {LINKS.map((link) => {
          const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
          return (
            <li key={link.href}>
              <Link
                href={link.href}
                className={active ? `${styles.item} ${styles.active}` : styles.item}
                aria-current={active ? "page" : undefined}
              >
                {link.label}
                {"stub" in link && link.stub ? (
                  <span className={styles.stub}>planned</span>
                ) : null}
              </Link>
            </li>
          );
        })}
      </ul>
      <div className={styles.meta}>
        <span className={styles.role}>Role simulator: Maker</span>
        <span className={styles.env}>v0.1-skeleton · mock queue</span>
      </div>
    </nav>
  );
}
