export default function SignalBadge({ signal, confidence, size = "md" }) {
  const colors = {
    BUY: "bg-buy/20 text-buy border-buy/30",
    SELL: "bg-sell/20 text-sell border-sell/30",
    HOLD: "bg-hold/20 text-hold border-hold/30",
  };
  const sizes = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
    lg: "text-base px-4 py-1.5 font-bold",
  };

  return (
    <span className={`border rounded-full font-semibold tracking-wide ${colors[signal] ?? colors.HOLD} ${sizes[size]}`}>
      {signal}
      {confidence && size !== "sm" && (
        <span className="ml-1.5 opacity-70 font-normal text-xs">{confidence}</span>
      )}
    </span>
  );
}
