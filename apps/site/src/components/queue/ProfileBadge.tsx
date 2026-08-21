import type { TransactionProfile } from "@/lib/mock/types";
import { profileLabel } from "@/lib/mock/labels";

export function ProfileBadge({ profile }: { profile: TransactionProfile }) {
  return (
    <span
      className="inline-flex max-w-full items-center rounded border border-rule bg-bench px-2 py-0.5 text-xs font-medium text-slate"
      title={profile}
    >
      <span className="sr-only">Transaction profile: </span>
      {profileLabel(profile)}
    </span>
  );
}
