import { useState } from "react";
import { Search, Paperclip } from "lucide-react";
import Avatar from "../ui/Avatar";
import Button from "../ui/Button";
import Input from "../ui/Input";
import SuggestionItem from "../SuggestionItem/SuggestionItem";
import "./FashionChat.css";
import { useNavigate } from "react-router-dom";
import { Message } from "../../types/message";
import { sendMessageToBackend } from "../../api/ChatService";
import { Send } from "lucide-react";

function FashionAIChat() {
  const [message, setMessage] = useState<string>("");
  const [messeages, setMesseages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleMessage = async () => {
    if (!message.trim()) return;

    // Add user message to chat
    const userMessage: Message = { text: message, sender: "user" };
    setMesseages((prev) => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      //Send backend & recieve bot response
      const botResponseText = await sendMessageToBackend(message);
      const botMessage: Message = { text: botResponseText, sender: "bot" };
      setMesseages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error finding messeage:", error);
      setMesseages((prev) => [
        ...prev,
        { text: "Error:Unable to reach server.", sender: "bot" },
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="fashion-chat-container">
      {/* Header */}
      <header className="fashion-chat-header">
        <div className="fashion-chat-logo" onClick={() => navigate("/")}>
          <div className="fashion-chat-logo">
            <div className="fashion-chat-logo-icon"></div>
            Fashion AI
          </div>
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
          {messeages.map((msg, index) => (
            <div key={index} className={`fashion-chat-message ${msg.sender}`}>
              <div className="fashion-chat-message-bubble">
                <p>{msg.text}</p>
              </div>
            </div>
          ))}
          {loading && <p className="fashion-chat-loading">Thinking...</p>}
        </div>

        {/* Message Input */}
        <div className="fashion-chat-input-container">
          <Input
            className="fashion-chat-input"
            placeholder="Type a messeage..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <div className="fashion-chat-input-actions">
            <Button variant="ghost" className="fashion-chat-attachment-button">
              <Paperclip className="fashion-chat-attachment-icon" />
            </Button>
            <Button
              onClick={handleMessage}
              disabled={loading}
              className="fashion-chat-send-button">
              Send!
            </Button>
          </div>
        </div>

        {/* Suggestions */}
        <div className="fashion-chat-suggestions">
          <h2 className="fashion-chat-suggestions-title">Suggestions</h2>
          <div className="fashion-chat-suggestions-grid">
            <SuggestionItem
              title="Women's fashion"
              subtitle="Women's fashion"
              image="https://placeholder.svg?height=48&width=48"
            />
            <SuggestionItem
              title="Men's fashion"
              subtitle="Men's fashion"
              image="https://placeholder.svg?height=48&width=48"
            />
            <SuggestionItem
              title="Shoes"
              subtitle="Shoes"
              image="https://placeholder.svg?height=48&width=48"
            />
            <SuggestionItem
              title="Bags"
              subtitle="Bags"
              image="https://placeholder.svg?height=48&width=48"
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default FashionAIChat;
