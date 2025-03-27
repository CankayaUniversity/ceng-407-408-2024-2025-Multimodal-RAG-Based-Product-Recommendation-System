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
  const [file, setFile] = useState<File | null>(null);
  const [image, setImage] = useState<string | undefined>(undefined);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);

      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreview(reader.result as string);
        setImage(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleMessage = async () => {
    if (!message.trim() && !image) return;


    const userMessage: Message = { text: message, sender: "user", imageBase64: image };
    setMessages((prev) => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      if (message.trim()) {
        const botResponseText = await sendMessageToBackend(message);
        setMessages((prev) => [
          ...prev,
          { text: botResponseText, sender: "bot", imageBase64: undefined }, // No image for the bot response
        ]);
      }

      if (image) {
        const imageData = { imageBase64: image };

        const fileResponse = await fetch("http://localhost:3001/upload", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(imageData),
        });

        const fileData = await fileResponse.json();
        if (fileData.success) {
          setMessages((prev) => [
            ...prev,
            { text: "Image uploaded successfully!", sender: "bot", imageBase64: image },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            { text: "Error: Image upload failed.", sender: "bot", imageBase64: undefined },
          ]);
        }
      }
    } catch (error) {
      console.error("Error communicating with backend:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Error: Unable to reach the server.", sender: "bot", imageBase64: undefined },
      ]);
    }

    setImage(undefined);
    setFilePreview(null);
    setFile(null);
    setLoading(false);
  };

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleMessage();
    }
  };

  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
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
                {msg.imageBase64 && (
                  <img
                    src={msg.imageBase64}
                    alt="Uploaded"
                    className="fashion-chat-image"
                  />
                )}
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
            onKeyPress={handleKeyPress}
          />
          {/* Display the image preview */}
          {filePreview && (
            <div className="fashion-chat-image-preview">
              <img src={filePreview} alt="Preview" className="fashion-chat-preview-image" />
            </div>
          )}
          <div className="fashion-chat-input-actions">
            <Button
              onClick={handleAttachmentClick}
              className="fashion-chat-attachment-button">
              <Paperclip size={20} className="fashion-chat-attachment-icon" />
            </Button>
            <Button
              onClick={handleMessage}
              disabled={loading || (!message.trim() && !image)}
              className="fashion-chat-send-button">
              <Send
                size={25}
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

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
    </div>
  );
}

export default FashionAIChat;
