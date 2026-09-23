"use client";

/**
 * The quantity mismatch, made physical.
 *
 * Both sides are the same pallet: a five-by-two grid of slots. The invoice
 * pallet is full; the bill of lading pallet is three short, and those three
 * empty slots are drawn as outlines. That gap is the entire product argument
 * in one glance — you see the missing goods rather than reading two numbers.
 *
 * Why counts and not size: 500 and 350 are in the ratio 10:7 exactly, so ten
 * cartons against seven is a true encoding. Drawing one big box and one small
 * box would scale *area* by roughly two, which overstates the difference —
 * the one place the brief is worth arguing with, because the page's whole
 * claim is that it reports figures faithfully.
 *
 * The cartons are decorative: the numbers beside them carry the data, so the
 * whole pallet is hidden from assistive technology.
 */

const COLUMNS = 5;
const ROWS = 2;
const SLOTS = COLUMNS * ROWS;

function Carton({ ghost }: { ghost: boolean }) {
  if (ghost) {
    return (
      <svg viewBox="0 0 40 32" className="h-full w-full text-signal" fill="none" aria-hidden>
        <rect
          x="1.5"
          y="1.5"
          width="37"
          height="29"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeDasharray="3 3"
          opacity="0.75"
        />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 40 32" className="h-full w-full" fill="none" aria-hidden>
      <rect x="1" y="1" width="38" height="30" className="fill-paper" />
      <rect x="1" y="1" width="38" height="30" stroke="currentColor" strokeWidth="1.5" />
      {/* Lid seam and tape, so it reads as a carton rather than a rectangle. */}
      <path d="M1 11h38" stroke="currentColor" strokeWidth="1.5" />
      <path d="M20 1v10" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function Pallet({ filled, align }: { filled: number; align: "left" | "right" }) {
  // Cartons stack bottom-up, the way they would on a real pallet, so the gaps
  // land on the top row.
  const bottomFilled = Math.min(filled, COLUMNS);
  const topFilled = Math.max(0, filled - COLUMNS);

  const slots = Array.from({ length: SLOTS }, (_, i) => {
    const row = Math.floor(i / COLUMNS); // 0 = top
    const col = i % COLUMNS;
    const isFilled = row === 0 ? col < topFilled : col < bottomFilled;
    // Bottom row settles before the top row.
    const order = row === 0 ? COLUMNS + col : col;
    return { i, isFilled, order };
  });

  return (
    <div
      aria-hidden
      data-pallet
      className={`mt-8 grid w-full max-w-[17rem] gap-1.5 lg:mt-10 lg:gap-2 ${
        align === "right" ? "ml-auto" : "mr-auto"
      }`}
      style={{ gridTemplateColumns: `repeat(${COLUMNS}, minmax(0, 1fr))` }}
    >
      {slots.map(({ i, isFilled, order }) => (
        <div key={i} className="aspect-[40/32]">
          {isFilled ? (
            // Three layers, each owned by exactly one thing. Draggable owns
            // the outer element's transform; the scroll timeline owns the
            // middle one; hover and press are CSS on the inner span. Two
            // systems writing transforms to the same node clobber each other —
            // a GSAP tween rewrites the whole matrix, so a drag offset would
            // silently reset to zero.
            <div
              data-carton
              className="h-full w-full text-ink lg:cursor-grab lg:active:cursor-grabbing"
            >
              <div data-fall data-order={order} className="h-full w-full">
                <span className="block h-full w-full transition-transform duration-200 ease-out lg:hover:-translate-y-1 lg:hover:rotate-[-3deg] lg:[.is-held_&]:scale-105">
                  <Carton ghost={false} />
                </span>
              </div>
            </div>
          ) : (
            <div data-ghost className="h-full w-full">
              <Carton ghost />
            </div>
          )}
        </div>
      ))}
      {/* The cartons need something to land on, or they read as floating. */}
      <div
        data-shelf
        className={`col-span-5 mt-2 h-px bg-rule ${align === "right" ? "origin-right" : "origin-left"}`}
      />
    </div>
  );
}
