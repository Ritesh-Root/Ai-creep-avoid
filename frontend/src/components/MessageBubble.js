import React from "react";

export default function MessageBubble({ message, side }) {
  const { type, text, imageUrl, analysis } = message;
  const isSender = side === "sender";

  const action = analysis?.action || "allow";
  const reason = analysis?.reason || "";
  const creepScore = analysis?.creep_score;

  const blurClass =
    !isSender && action === "blur"
      ? "blur-sm"
      : !isSender && action === "block"
      ? "blur-lg"
      : "";

  return (
    <div
      className={`flex ${isSender ? "justify-end" : "justify-start"} mb-3 glass-fade-in`}
    >
      <div className="max-w-xs lg:max-w-sm relative">
        {/* Message content */}
        <div
          className={`rounded-xl px-4 py-2 ${
            isSender
              ? "glass-bubble-sender"
              : "glass-bubble-receiver"
          }`}
        >
          {type === "text" && (
            <p className={blurClass}>{text}</p>
          )}
          {type === "image" && imageUrl && (
            <img
              src={imageUrl}
              alt="attachment"
              className={`max-h-48 rounded-lg ${blurClass}`}
            />
          )}
        </div>

        {/* Receiver-side overlays */}
        {!isSender && action === "blur" && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="glass-card-light text-yellow-300 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              {reason}
            </span>
          </div>
        )}

        {!isSender && action === "block" && (
          <div className="absolute inset-0 flex items-center justify-center rounded-xl" style={{ background: "rgba(220, 38, 38, 0.5)", backdropFilter: "blur(4px)" }}>
            <span className="bg-red-700/80 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              {reason}
            </span>
          </div>
        )}

        {/* Creep score badge on receiver side */}
        {!isSender && creepScore !== undefined && (
          <div className="mt-1 text-right">
            <span
              className={`text-xs font-mono px-2 py-0.5 rounded-md backdrop-blur-sm ${
                creepScore >= 0.7
                  ? "bg-red-500/20 text-red-300 border border-red-500/30"
                  : creepScore >= 0.4
                  ? "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30"
                  : "bg-green-500/20 text-green-300 border border-green-500/30"
              }`}
            >
              Score: {creepScore}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
