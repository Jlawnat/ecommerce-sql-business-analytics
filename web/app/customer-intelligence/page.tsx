import rawData from "../../public/data/customer-intelligence.json";
import type { Metadata } from "next";
import { ApplicationShell } from "@/components/application-shell";
import { CustomerIntelligence } from "@/components/customer-intelligence";
import { parseCustomerIntelligence } from "@/lib/contracts";

export const metadata: Metadata = {
  title: "Customer intelligence",
};

export default function CustomerIntelligencePage() {
  const data = parseCustomerIntelligence(rawData);
  return <ApplicationShell><CustomerIntelligence data={data} /></ApplicationShell>;
}
