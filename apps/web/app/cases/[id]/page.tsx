import { LiveCaseWorkbench } from "@/components/case/LiveCaseWorkbench";

export default async function CasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <LiveCaseWorkbench caseId={id} />;
}
