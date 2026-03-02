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
    <div className="flex flex-col h-full border border-gray-300 rounded-lg overflow-hidden bg-white">
      {/* Header */}
      <div
        className={`px-4 py-3 font-bold text-white ${
          isSender ? "bg-blue-600" : "bg-green-600"
        }`}
      >
        {title}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1 bg-gray-50">
        {messages.length === 0 && (
          <p className="text-center text-gray-400 mt-10 text-sm">
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
          className="flex items-center gap-2 p-3 border-t border-gray-200"
        >
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Type a message…"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-full p-2 text-sm"
            title="Upload image"
          >
            📎
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
            className="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-4 py-2 text-sm font-semibold"
          >
            Send
          </button>
        </form>
      ) : (
        <div className="p-3 border-t border-gray-200 flex justify-center">
          <button
            onClick={onReply}
            className="bg-green-500 hover:bg-green-600 text-white rounded-full px-6 py-2 text-sm font-semibold"
          >
            Reply
          </button>
        </div>
      )}
    </div>
  );
}
