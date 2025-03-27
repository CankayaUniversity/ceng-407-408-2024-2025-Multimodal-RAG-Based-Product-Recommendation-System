import { useState, useEffect, useRef } from "react";
import { Search, Paperclip, Send } from "lucide-react";
import Avatar from "../ui/Avatar";
import Button from "../ui/Button";
import Input from "../ui/Input";
import SuggestionItem from "../SuggestionItem/SuggestionItem";
import "./FashionChat.css";
import { useNavigate } from "react-router-dom";
import { Message } from "../../types/message";
import { sendMessageToBackend } from "../../api/ChatService";

function FashionAIChat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleMessage = async () => {
    if (!message.trim()) return;

    const userMessage: Message = { text: message, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const botResponseText = await sendMessageToBackend(message);
      setMessages((prev) => [
        ...prev,
        { text: botResponseText, sender: "bot" },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Error: Unable to reach server.", sender: "bot" },
      ]);
    }
    setLoading(false);
  };

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleMessage();
    }
  };

  return (
    <div className="fashion-chat-container">
      {/* Header */}
      <header className="fashion-chat-header">
        <div className="fashion-chat-logo" onClick={() => navigate("/")}>
          <div className="fashion-chat-logo-icon"></div>
          Fashion AI
        </div>
        <div className="fashion-chat-search-container">
          <Search className="fashion-chat-search-icon" />
          <Input className="fashion-chat-search-input" placeholder="Search" />
        </div>
        <div className="fashion-chat-header-actions">
          <Button variant="ghost" className="fashion-chat-help-button">
            Help
          </Button>
          <Avatar
            image="https://placeholder.svg?height=32&width=32"
            fallback="U"
            alt="User"
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="fashion-chat-main">
        <h1 className="fashion-chat-title">Chat with me</h1>

        {/* Chat Messages */}
        <div className="fashion-chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`fashion-chat-message ${msg.sender}`}>
              <div className="fashion-chat-message-bubble">
                <p>{msg.text}</p>
              </div>
            </div>
          ))}
          {loading && <p className="fashion-chat-loading">Thinking...</p>}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="fashion-chat-input-container">
          <Input
            className="fashion-chat-input"
            placeholder="Type a message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress} // Allow sending with Enter key
          />
          <div className="fashion-chat-input-actions">
            <Button className="fashion-chat-attachment-button">
              <Paperclip size={20} className="fashion-chat-attachment-icon" />
            </Button>
            <Button
              onClick={handleMessage}
              disabled={loading || !message.trim()}
              className="fashion-chat-send-button">
              <Send
                size={20}
                color="white"
                className="fashion-chat-send-icon"
              />
            </Button>
          </div>
        </div>

        {/* Suggestions */}
        <div className="fashion-chat-suggestions">
          <h2 className="fashion-chat-suggestions-title">Suggestions</h2>
          <div className="fashion-chat-suggestions-grid">
            {["Women's fashion", "Men's fashion", "Shoes", "Bags"].map(
              (category) => (
                <SuggestionItem
                  key={category}
                  title={category}
                  subtitle={category}
                  image="https://placeholder.svg?height=48&width=48"
                />
              )
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default FashionAIChat;
