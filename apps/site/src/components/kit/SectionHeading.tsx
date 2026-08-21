import { cn } from "@/lib/utils";
import { Eyebrow } from "./Eyebrow";

/** Hangs in columns 1–4. Never centered. */
export function SectionHeading({
  eyebrow,
  children,
  level = "h2",
  className,
}: {
  eyebrow?: string;
  children: React.ReactNode;
  level?: "h1" | "h2" | "h3";
  className?: string;
}) {
  const size = level === "h1" ? "text-h1" : level === "h2" ? "text-h2" : "text-h3";
  const Tag = level;

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      {eyebrow ? <Eyebrow>{eyebrow}</Eyebrow> : null}
      <Tag className={cn(size, "font-mono text-ink text-balance")}>{children}</Tag>
    </div>
  );
}
