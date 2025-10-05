"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatbotInteractionInDB, UUID } from "@/lib/models";
import { askChatbot } from "@/lib/api";

interface ChatbotWidgetProps {
  userId: UUID;
  history: ChatbotInteractionInDB[];
  onNewInteraction: () => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ userId, history, onNewInteraction }) => {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userQuery = input;
    setInput("");
    setLoading(true);
    setError(null);

    try {
      // Optimistically update history (optional, but good for UX)
      // For simplicity, we'll refetch all history after interaction
      await askChatbot(userQuery);
      onNewInteraction(); // Trigger parent to refetch history
    } catch (err: any) {
      console.error("Chatbot error:", err);
      setError(err.message || "Failed to get chatbot response.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-h-[600px] min-h-[400px] bg-gray-50 rounded-lg shadow-inner">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {history.length === 0 && !loading && (
          <p className="text-center text-gray-500">Ask me anything about financial literacy!</p>
        )}
        {history.map((interaction) => (
          <div key={interaction.id} className="flex flex-col">
            <div className="self-end bg-blue-500 text-white p-3 rounded-lg max-w-[80%] break-words shadow-sm">
              {interaction.query}
            </div>
            <div className="self-start bg-gray-200 text-gray-800 p-3 rounded-lg max-w-[80%] mt-2 break-words shadow-sm">
              {interaction.response}
            </div>
          </div>
        ))}
        {loading && (
          <div className="self-start bg-gray-200 text-gray-800 p-3 rounded-lg max-w-[80%] mt-2 shadow-sm">
            Thinking...
          </div>
        )}
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          disabled={loading}
        />
        <button
          type="submit"
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          disabled={loading}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatbotWidget;
