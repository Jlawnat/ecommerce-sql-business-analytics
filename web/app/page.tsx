import rawData from "../public/data/executive-overview.json";
import { ApplicationShell } from "@/components/application-shell";
import { ExecutiveOverview } from "@/components/executive-overview";
import { parseExecutiveOverview } from "@/lib/contracts";

export default function Home() {
  const data = parseExecutiveOverview(rawData);
  return <ApplicationShell><ExecutiveOverview data={data} /></ApplicationShell>;
}
