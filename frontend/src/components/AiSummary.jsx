import { Sparkles } from "lucide-react";

export default function AiSummary({ summary }) {
  if (!summary) return null;

  const paragraphs = summary.split("\n\n").filter(Boolean);

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-3">
      <div className="flex items-center gap-2">
        <Sparkles size={15} className="text-accent" />
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          AI Intelligence Summary
        </h3>
      </div>
      <div className="space-y-3 text-sm text-slate-300 leading-relaxed">
        {paragraphs.map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
    </div>
  );
}
