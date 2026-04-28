import { Sparkles } from "lucide-react";

const PROVIDER_LABELS = {
  anthropic: { label: "Claude", color: "text-violet-400 bg-violet-400/10 border-violet-400/20" },
  gemini: { label: "Gemini", color: "text-blue-400 bg-blue-400/10 border-blue-400/20" },
};

export default function AiSummary({ summary, provider }) {
  if (!summary) return null;

  const paragraphs = summary.split("\n\n").filter(Boolean);
  const badge = provider ? PROVIDER_LABELS[provider] : null;

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles size={15} className="text-accent" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            AI Intelligence Summary
          </h3>
        </div>
        {badge && (
          <span className={`text-xs font-medium px-2 py-0.5 border rounded-full ${badge.color}`}>
            {badge.label}
          </span>
        )}
      </div>
      <div className="space-y-3 text-sm text-slate-300 leading-relaxed">
        {paragraphs.map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
    </div>
  );
}
