import rawData from "../../public/data/delivery-satisfaction.json";
import type { Metadata } from "next";
import { ApplicationShell } from "@/components/application-shell";
import { DeliverySatisfaction } from "@/components/delivery-satisfaction";
import { parseDeliverySatisfaction } from "@/lib/contracts";

export const metadata: Metadata = {
  title: "Delivery & satisfaction",
};

export default function DeliverySatisfactionPage() {
  const data = parseDeliverySatisfaction(rawData);
  return <ApplicationShell><DeliverySatisfaction data={data} /></ApplicationShell>;
}
