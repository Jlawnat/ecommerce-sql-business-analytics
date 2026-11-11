export type SalesWindow = "all" | "2017" | "2018";

const options: Array<{ value: SalesWindow; label: string }> = [
  { value: "all", label: "Full window" },
  { value: "2017", label: "2017" },
  { value: "2018", label: "2018" },
];

export function FilterToolbar({ value, onChange }: { value: SalesWindow; onChange: (value: SalesWindow) => void }) {
  return (
    <div className="filter-toolbar">
      <div><strong>Sales window</strong><span>Updates order, value, average and trend</span></div>
      <div className="segmented-control" role="group" aria-label="Sales observation window">
        {options.map((option) => <button key={option.value} type="button" aria-pressed={value === option.value} onClick={() => onChange(option.value)}>{option.label}</button>)}
      </div>
    </div>
  );
}
