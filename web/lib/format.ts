export const formatInteger = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
export const formatMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "BRL",
  currencyDisplay: "code",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
export const formatCompactMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "BRL",
  currencyDisplay: "code",
  notation: "compact",
  maximumFractionDigits: 2,
});

export function labelCategory(value: string) {
  if (value === "[uncategorized]") return "Uncategorized";
  return value.split("_").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
}
