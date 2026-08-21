import { cn } from "@/lib/utils";

export function Eyebrow({
  children,
  className,
  tone = "slate",
}: {
  children: React.ReactNode;
  className?: string;
  tone?: "slate" | "paper";
}) {
  return (
    <p className={cn("text-label", tone === "slate" ? "text-slate" : "text-rule", className)}>
      {children}
    </p>
  );
}
