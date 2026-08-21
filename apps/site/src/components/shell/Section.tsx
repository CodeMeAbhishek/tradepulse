import { cn } from "@/lib/utils";

/**
 * One numbered section of the ledger. The data attributes are what the rail
 * reads; the padding is the only vertical rhythm on the site.
 */
export function Section({
  number,
  name,
  children,
  className,
  id,
}: {
  number: string;
  name: string;
  children: React.ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <section
      id={id}
      data-section-number={number}
      data-section-name={name}
      className={cn("px-6 py-[80px] lg:px-10 lg:py-[112px]", className)}
    >
      <div className="mx-auto w-full max-w-[1600px]">{children}</div>
    </section>
  );
}
