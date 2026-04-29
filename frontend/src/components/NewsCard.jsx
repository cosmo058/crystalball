import { ExternalLink } from "lucide-react";

function formatDate(raw) {
  if (!raw) return null;
  try {
    const d = new Date(raw);
    if (isNaN(d)) return null;
    const now = new Date();
    const diffDays = Math.floor((now - d) / 86400000);
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    const sameYear = d.getFullYear() === now.getFullYear();
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      ...(!sameYear && { year: "numeric" }),
    });
  } catch {
    return null;
  }
}

const sentimentColors = {
  POSITIVE: "text-buy bg-buy/10 border-buy/20",
  NEGATIVE: "text-sell bg-sell/10 border-sell/20",
  NEUTRAL: "text-slate-400 bg-slate-400/10 border-slate-400/20",
};

const sentimentLabel = {
  POSITIVE: "P",
  NEGATIVE: "N",
  NEUTRAL: "—",
};

export default function NewsCard({ news, enriching }) {
  if (!news?.length) return null;

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Recent News
        </h3>
        {enriching && (
          <span className="flex items-center gap-1.5 text-[10px] text-indigo-400">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Analyzing sentiment…
          </span>
        )}
      </div>

      <div className="space-y-2">
        {news.map((item, i) => (
          <a
            key={i}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-surface transition group"
          >
            <span className="relative shrink-0 mt-0.5">
              <span
                className={`inline-block text-[10px] font-bold px-1.5 py-0.5 border rounded ${sentimentColors[item.sentiment]}`}
              >
                {sentimentLabel[item.sentiment]}
              </span>
              {item.sentiment_reason && (
                <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-indigo-500" />
              )}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 group-hover:text-white leading-snug line-clamp-2 transition">
                {item.title}
              </p>
              {item.sentiment_reason && (
                <p className="text-xs text-indigo-400/80 mt-0.5 leading-snug">
                  {item.sentiment_reason}
                </p>
              )}
              <p className="text-xs text-slate-500 mt-0.5">
                {item.source}
                {formatDate(item.published) && (
                  <span className="text-slate-600"> · {formatDate(item.published)}</span>
                )}
              </p>
            </div>
            <ExternalLink size={13} className="shrink-0 text-slate-600 group-hover:text-slate-400 mt-1 transition" />
          </a>
        ))}
      </div>
    </div>
  );
}
