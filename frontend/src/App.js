import React, { useState, useCallback } from "react";
import ChatPanel from "./components/ChatPanel";
import { analyzeText, analyzeImage, sendReply } from "./api";
import "./App.css";

const SENDER_ID = "user1";
const RECEIVER_ID = "user2";

let nextId = 1;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");

  const addMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, { ...msg, id: nextId++ }]);
  }, []);

  const handleSendText = useCallback(
    async (text) => {
      // Add message immediately (optimistic)
      const msg = { type: "text", text, analysis: null };
      const id = nextId;
      addMessage(msg);
      setInputValue("");

      try {
        const result = await analyzeText(SENDER_ID, RECEIVER_ID, text);
        setMessages((prev) =>
          prev.map((m) => (m.id === id ? { ...m, analysis: result } : m))
        );
      } catch {
        // If backend unreachable, show message normally
        setMessages((prev) =>
          prev.map((m) =>
            m.id === id
              ? { ...m, analysis: { action: "allow", reason: "", creep_score: 0 } }
              : m
          )
        );
      }
    },
    [addMessage]
  );

  const handleImageUpload = useCallback(
    async (file) => {
      const imageUrl = URL.createObjectURL(file);
      const msg = { type: "image", imageUrl, text: file.name, analysis: null };
      const id = nextId;
      addMessage(msg);

      try {
        const result = await analyzeImage(SENDER_ID, RECEIVER_ID, file);
        setMessages((prev) =>
          prev.map((m) => (m.id === id ? { ...m, analysis: result } : m))
        );
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === id
              ? { ...m, analysis: { action: "allow", reason: "", creep_score: 0 } }
              : m
          )
        );
      }
    },
    [addMessage]
  );

  const handleReply = useCallback(async () => {
    try {
      await sendReply(RECEIVER_ID, SENDER_ID);
    } catch {
      // Ignore errors silently
    }
  }, []);

  return (
    <div className="app-container bg-gray-100">
      {/* Header */}
      <header className="bg-gray-900 text-white text-center py-3">
        <h1 className="text-xl font-bold tracking-wide">
          🛡️ SmartShield AI — Content Moderation Demo
        </h1>
      </header>

      {/* Split-screen panels */}
      <div className="flex-1 flex gap-4 p-4 min-h-0">
        <div className="flex-1 min-w-0">
          <ChatPanel
            title="Sender (You)"
            side="sender"
            messages={messages}
            onSend={handleSendText}
            onImageUpload={handleImageUpload}
            inputValue={inputValue}
            onInputChange={setInputValue}
          />
        </div>
        <div className="flex-1 min-w-0">
          <ChatPanel
            title="Receiver"
            side="receiver"
            messages={messages}
            onReply={handleReply}
          />
        </div>
      </div>
    </div>
  );
}

export default App;

