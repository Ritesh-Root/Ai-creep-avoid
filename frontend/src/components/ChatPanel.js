import React, { useRef } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatPanel({
  title,
  side,
  messages,
  onSend,
  onImageUpload,
  onReply,
  inputValue,
  onInputChange,
}) {
  const fileInputRef = useRef(null);
  const isSender = side === "sender";

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSend && inputValue.trim()) {
      onSend(inputValue.trim());
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && onImageUpload) {
      onImageUpload(file);
    }
    e.target.value = "";
  };

  return (
    <div className="glass-card flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div
        className={`px-4 py-3 font-bold text-white ${
          isSender
            ? "bg-gradient-to-r from-indigo-500/30 to-purple-500/30"
            : "bg-gradient-to-r from-emerald-500/30 to-teal-500/30"
        } border-b border-white/10`}
      >
        <div className="flex items-center gap-2">
          {isSender ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          )}
          {title}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1">
        {messages.length === 0 && (
          <p className="text-center text-white/30 mt-10 text-sm">
            No messages yet
          </p>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} side={side} />
        ))}
      </div>

      {/* Input area (sender) or Reply button (receiver) */}
      {isSender ? (
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 p-3 border-t border-white/10"
        >
          <input
            type="text"
            className="glass-input flex-1 rounded-full px-4 py-2 text-sm"
            placeholder="Type a message..."
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="glass-btn rounded-full p-2 text-sm"
            title="Upload image"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.414a4 4 0 00-5.656-5.656l-6.415 6.414a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          <button
            type="submit"
            className="glass-btn rounded-full px-4 py-2 text-sm font-semibold"
          >
            Send
          </button>
        </form>
      ) : (
        <div className="p-3 border-t border-white/10 flex justify-center">
          <button
            onClick={onReply}
            className="glass-btn glass-btn-success rounded-full px-6 py-2 text-sm font-semibold text-white"
          >
            Reply
          </button>
        </div>
      )}
    </div>
  );
}
