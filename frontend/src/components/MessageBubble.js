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
      className={`flex ${isSender ? "justify-end" : "justify-start"} mb-3`}
    >
      <div className="max-w-xs lg:max-w-sm relative">
        {/* Message content */}
        <div
          className={`rounded-lg px-4 py-2 shadow ${
            isSender
              ? "bg-blue-500 text-white"
              : "bg-gray-200 text-gray-900"
          }`}
        >
          {type === "text" && (
            <p className={blurClass}>{text}</p>
          )}
          {type === "image" && imageUrl && (
            <img
              src={imageUrl}
              alt="attachment"
              className={`max-h-48 rounded ${blurClass}`}
            />
          )}
        </div>

        {/* Receiver-side overlays */}
        {!isSender && action === "blur" && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="bg-yellow-400 text-yellow-900 text-xs font-semibold px-2 py-1 rounded shadow">
              ⚠ {reason}
            </span>
          </div>
        )}

        {!isSender && action === "block" && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-600 bg-opacity-60 rounded-lg">
            <span className="bg-red-700 text-white text-xs font-bold px-2 py-1 rounded shadow">
              🚫 {reason}
            </span>
          </div>
        )}

        {/* Creep score badge on receiver side */}
        {!isSender && creepScore !== undefined && (
          <div className="mt-1 text-right">
            <span
              className={`text-xs font-mono px-1.5 py-0.5 rounded ${
                creepScore >= 70
                  ? "bg-red-100 text-red-700"
                  : creepScore >= 40
                  ? "bg-yellow-100 text-yellow-700"
                  : "bg-green-100 text-green-700"
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
