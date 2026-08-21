import { CaseWorkbench } from "@/components/case/CaseWorkbench";

export default async function CasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CaseWorkbench caseId={id} />;
}
