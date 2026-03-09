import React, { useState, useCallback, useRef } from "react";
import ChatPanel from "./components/ChatPanel";
import { analyzeText, analyzeImage, sendReply } from "./api";
import "./App.css";

const SENDER_ID = "user1";
const RECEIVER_ID = "user2";

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const nextIdRef = useRef(1);

  const addMessage = useCallback((msg) => {
    const id = nextIdRef.current++;
    setMessages((prev) => [...prev, { ...msg, id }]);
    return id;
  }, []);

  const handleSendText = useCallback(
    async (text) => {
      const msg = { type: "text", text, analysis: null };
      const id = addMessage(msg);
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
      const id = addMessage(msg);

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
      await sendReply(SENDER_ID, RECEIVER_ID);
    } catch {
      // Ignore errors silently
    }
  }, []);

  return (
    <div className="app-container">
      {/* Background orbs for depth */}
      <div className="bg-orb bg-orb-1" />
      <div className="bg-orb bg-orb-2" />
      <div className="bg-orb bg-orb-3" />

      {/* Header */}
      <header className="glass-header text-white text-center py-3 relative z-10">
        <h1 className="text-xl font-bold tracking-wide flex items-center justify-center gap-2">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
            />
          </svg>
          SmartShield AI -- Content Moderation
        </h1>
      </header>

      {/* Split-screen panels */}
      <div className="flex-1 flex gap-4 p-4 min-h-0 relative z-10">
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

