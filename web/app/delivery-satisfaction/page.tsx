import rawData from "../../public/data/delivery-satisfaction.json";
import { ApplicationShell } from "@/components/application-shell";
import { DeliverySatisfaction } from "@/components/delivery-satisfaction";
import { parseDeliverySatisfaction } from "@/lib/contracts";

export default function DeliverySatisfactionPage() {
  const data = parseDeliverySatisfaction(rawData);
  return <ApplicationShell><DeliverySatisfaction data={data} /></ApplicationShell>;
}
