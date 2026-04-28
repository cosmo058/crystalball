import { ExternalLink } from "lucide-react";

const sentimentColors = {
  POSITIVE: "text-buy bg-buy/10 border-buy/20",
  NEGATIVE: "text-sell bg-sell/10 border-sell/20",
  NEUTRAL: "text-slate-400 bg-slate-400/10 border-slate-400/20",
};

export default function NewsCard({ news }) {
  if (!news?.length) return null;

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Recent News</h3>
      <div className="space-y-2">
        {news.map((item, i) => (
          <a
            key={i}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-surface transition group"
          >
            <span
              className={`shrink-0 mt-0.5 text-[10px] font-bold px-1.5 py-0.5 border rounded ${sentimentColors[item.sentiment]}`}
            >
              {item.sentiment[0]}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 group-hover:text-white leading-snug line-clamp-2 transition">
                {item.title}
              </p>
              <p className="text-xs text-slate-500 mt-1">{item.source}</p>
            </div>
            <ExternalLink size={13} className="shrink-0 text-slate-600 group-hover:text-slate-400 mt-1 transition" />
          </a>
        ))}
      </div>
    </div>
  );
}
