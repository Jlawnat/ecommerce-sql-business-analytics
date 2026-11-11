import type { Metadata } from "next";
import { ApplicationShell } from "@/components/application-shell";
import { MethodologyEvidence } from "@/components/methodology-evidence";

export const metadata: Metadata = {
  title: "Methodology & evidence",
  description: "Trace Olist dashboard metrics through source data, SQL, statistical methods, validation and aggregate publishing.",
};

export default function MethodologyPage() {
  return <ApplicationShell><MethodologyEvidence /></ApplicationShell>;
}
