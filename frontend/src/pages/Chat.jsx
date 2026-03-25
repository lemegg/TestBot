import React, { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Knowledge Assistant. How can I help you today?',
    }
  ]);
  const [loading, setLoading] = useState(false);
  const { getToken } = useAuth();

  const handleSendMessage = async (text) => {
    const userMsg = { sender: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    console.log("Sending question:", text);

    try {
      const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const api_url = isLocal ? `http://${window.location.hostname}:8001/api/chat` : '/api/chat';

      const token = await getToken();
      const response = await fetch(api_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) throw new Error('Failed to fetch');

      const data = await response.json();
      console.log("Response:", data);
      setMessages((prev) => [...prev, {
        sender: 'bot',
        query_log_id: data.query_log_id,
        answer: data.answer,
        sources: data.sources,
      }]);
    } catch (error) {
      setMessages((prev) => [...prev, {
        sender: 'bot',
        text: 'Server error. Please try again.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-page-container">
      <header className="page-header">
        <h2>AI Knowledge Chat</h2>
      </header>
      <div className="chat-interface">
        <ChatWindow messages={messages} isThinking={loading} />
        <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
};

export default Chat;
