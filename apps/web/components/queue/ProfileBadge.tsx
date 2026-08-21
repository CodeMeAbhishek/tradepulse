import type { TransactionProfile } from "@/lib/mock/types";
import { profileLabel } from "@/lib/mock/labels";

export function ProfileBadge({ profile }: { profile: TransactionProfile }) {
  return (
    <span
      className="inline-flex max-w-full items-center rounded border border-slate-600 bg-slate-900 px-2 py-0.5 text-xs font-medium text-slate-200"
      title={profile}
    >
      <span className="sr-only">Transaction profile: </span>
      {profileLabel(profile)}
    </span>
  );
}
