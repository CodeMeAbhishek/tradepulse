import Image from "next/image";

type ShotData = { src: string; width: number; height: number; alt: string };

/**
 * A screenshot of the live product: a single hairline rule, no shadow, no
 * browser chrome. The frame carries the only rounded corner on the page — the
 * blocks elsewhere stay hard-edged. The captured images are flattened square
 * (see scratchpad/recapture.cjs) so the frame's own radius does the clipping
 * and the product's card corners never show through as pale gaps.
 *
 * These are dense tables; scaled to a phone they turn into grey noise, so
 * below `lg` the frame scrolls sideways and the image keeps a legible width.
 */
export function Shot({
  shot,
  caption,
  priority = false,
  sizes = "(min-width: 1024px) 60vw, 100vw",
  className = "",
}: {
  shot: ShotData;
  caption?: string;
  priority?: boolean;
  sizes?: string;
  className?: string;
}) {
  return (
    <figure className={`min-w-0 ${className}`}>
      <div className="overflow-x-auto rounded-[10px] border border-rule">
        <div className="min-w-[40rem] lg:min-w-0">
          <Image
            src={shot.src}
            width={shot.width}
            height={shot.height}
            alt={shot.alt}
            sizes={sizes}
            priority={priority}
            className="h-auto w-full"
          />
        </div>
      </div>
      {caption && (
        <figcaption className="type-label mt-4 text-mute">
          {caption}
          <span className="lg:hidden"> Scroll sideways for the rest.</span>
        </figcaption>
      )}
    </figure>
  );
}
