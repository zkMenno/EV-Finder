import type { QualityTier } from "@ev/schema";

const STYLE: Record<QualityTier, string> = {
  checked: "bg-green-100 text-green-900 border-green-700",
  sourced: "bg-blue-100 text-blue-900 border-blue-700",
  "single-source": "bg-amber-100 text-amber-950 border-amber-700",
};

export function QualityBadge({ tier, label, help }: { tier: QualityTier; label: string; help: string }) {
  return (
    <span
      className={`inline-block whitespace-nowrap rounded-full border px-2 py-0.5 text-xs font-medium ${STYLE[tier]}`}
      title={help}
    >
      {label}
      <span className="sr-only">: {help}</span>
    </span>
  );
}
