import rawData from "../../public/data/customer-intelligence.json";
import { ApplicationShell } from "@/components/application-shell";
import { CustomerIntelligence } from "@/components/customer-intelligence";
import { parseCustomerIntelligence } from "@/lib/contracts";

export default function CustomerIntelligencePage() {
  const data = parseCustomerIntelligence(rawData);
  return <ApplicationShell><CustomerIntelligence data={data} /></ApplicationShell>;
}
