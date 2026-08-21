import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { motion, useScroll, useSpring } from "motion/react";
import { site } from "@/content/site";
import { DUR, EASE } from "@/lib/motion";

export function TopBar() {
  const [scrolled, setScrolled] = useState(false);
  const { scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 120, damping: 30 });

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className="sticky top-0 z-50 h-[68px] bg-bench">
      <div className="flex h-[68px] items-center gap-10 px-6 lg:pl-[104px]">
        <Link
          to="/"
          className="font-mono text-ink"
          style={{ fontSize: "18px", letterSpacing: "0.06em" }}
        >
          {site.mark} {site.name}
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {site.nav.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="group relative pb-1 text-slate transition-colors duration-[120ms] hover:text-ink"
              style={{ fontSize: "15px" }}
              activeProps={{ className: "text-ink" }}
            >
              {item.label}
              <span
                aria-hidden
                className="absolute bottom-0 left-0 h-px w-full origin-left scale-x-0 bg-ink transition-transform duration-[180ms] group-hover:scale-x-100 group-focus-visible:scale-x-100"
              />
            </Link>
          ))}
        </nav>

        <Link
          to={site.action.to}
          className="group relative ml-auto pb-1 text-ink"
          style={{ fontSize: "15px" }}
        >
          {site.action.label}
          <span
            aria-hidden
            className="absolute bottom-0 left-0 h-px w-full origin-left scale-x-0 bg-ink transition-transform duration-[180ms] group-hover:scale-x-100 group-focus-visible:scale-x-100"
          />
        </Link>
      </div>

      <motion.div
        className="h-px w-full origin-left"
        style={{ backgroundColor: scrolled ? "var(--ink)" : "var(--rule)" }}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: DUR.ruleDraw, ease: EASE.out }}
      />
      {scrolled ? (
        <motion.div className="h-px origin-left bg-ink" style={{ scaleX: progress }} />
      ) : null}
    </header>
  );
}
