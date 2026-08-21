import { useMemo, useState } from "react";
import type { DocumentCompletenessItem, TransactionProfile } from "@/lib/mock/types";
import { PROFILE_CHECKLIST_FIXTURES } from "@/lib/mock/profiles";
import { documentStateLabel, profileLabel } from "@/lib/mock/labels";
import { ProfileBadge } from "@/components/queue/ProfileBadge";

const PROFILE_OPTIONS: TransactionProfile[] = [
  "INVOICE_ONLY_PRE_REVIEW",
  "POST_SHIPMENT_DOCUMENT_REVIEW",
  "LC_DOCUMENT_REVIEW",
  "ENHANCED_TRADE_HOUSE_REVIEW",
];

export function DocumentUploadPanel({
  initialProfile,
  initialFiles,
}: {
  initialProfile: TransactionProfile;
  initialFiles: Array<{ name: string; documentType: string; sizeLabel: string }>;
}) {
  const [profile, setProfile] = useState<TransactionProfile>(initialProfile);
  const [files, setFiles] = useState(initialFiles);

  const checklist: DocumentCompletenessItem[] = useMemo(
    () => PROFILE_CHECKLIST_FIXTURES[profile],
    [profile],
  );

  return (
    <section className="rounded border border-rule bg-paper p-4" aria-labelledby="upload-heading">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="upload-heading" className="text-lg font-semibold text-ink">
            Upload & document policy checklist
          </h2>
          <p className="mt-1 text-sm text-slate">
            Checklist states come from configured profile fixtures. Missing optional documents do
            not block a case. Commercial Invoice is always required.
          </p>
        </div>
        <ProfileBadge profile={profile} />
      </div>

      <label className="mb-4 block text-sm text-slate">
        Transaction profile
        <select
          className="mt-1 w-full max-w-md rounded border border-rule bg-bench px-3 py-2 text-ink"
          value={profile}
          onChange={(e) => setProfile(e.target.value as TransactionProfile)}
        >
          {PROFILE_OPTIONS.map((p) => (
            <option key={p} value={p}>
              {profileLabel(p)}
            </option>
          ))}
        </select>
      </label>

      <div className="mb-4">
        <label className="block text-sm text-slate">
          Multi-file upload (local demo only — not sent to external APIs)
          <input
            type="file"
            multiple
            className="mt-1 block w-full text-sm text-slate file:mr-3 file:rounded file:border-0 file:bg-bench file:px-3 file:py-1.5 file:text-ink"
            onChange={(e) => {
              const list = Array.from(e.target.files ?? []).map((f) => ({
                name: f.name,
                documentType: "UPLOADED_LOCAL",
                sizeLabel: `${Math.max(1, Math.round(f.size / 1024))} KB`,
              }));
              if (list.length) setFiles((prev) => [...prev, ...list]);
            }}
          />
        </label>
        <ul className="mt-2 space-y-1 text-sm text-slate">
          {files.map((f) => (
            <li key={`${f.name}-${f.sizeLabel}`} className="font-mono text-xs">
              {f.name} · {f.documentType} · {f.sizeLabel}
            </li>
          ))}
          {files.length === 0 ? <li className="text-slate">No files listed yet.</li> : null}
        </ul>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wide text-slate">
            <tr>
              <th className="py-2 pr-3">Document</th>
              <th className="py-2 pr-3">Policy state</th>
              <th className="py-2 pr-3">Blocks case?</th>
              <th className="py-2">Reason</th>
            </tr>
          </thead>
          <tbody>
            {checklist.map((item) => (
              <tr key={item.documentType} className="border-t border-rule align-top">
                <td className="py-2.5 pr-3 text-slate">{item.label}</td>
                <td className="py-2.5 pr-3 font-mono text-xs text-ink">
                  {documentStateLabel(item.state)}
                </td>
                <td className="py-2.5 pr-3 text-slate">
                  {item.blocker ? "Yes — required for this profile" : "No"}
                </td>
                <td className="py-2.5 text-slate">{item.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
