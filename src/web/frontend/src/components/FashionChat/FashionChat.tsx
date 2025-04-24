import { useState, useEffect, useRef } from "react";
import { Paperclip, Send } from "lucide-react";
import Avatar from "../ui/Avatar";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Header from "../Header/Header";
import "./FashionChat.css";
import { useNavigate } from "react-router-dom";
import { Message } from "../../types/message";
import { sendMessageToBackend } from "../../api/ChatService";

const valid_categories = [
  "clip_BASICS",
  "clip_BLAZERS",
  "clip_DRESSES_JUMPSUITS",
  "clip_JACKETS",
  "clip_KNITWEAR",
  "clip_men_BLAZERS",
  "clip_men_HOODIES_SWEATSHIRTS",
  "clip_men_LINEN",
  "clip_men_OVERSHIRTS",
  "clip_men_POLO_SHIRTS",
  "clip_men_SHIRTS",
  "clip_men_SHOES",
  "clip_men_SHORTS",
  "clip_men_SWEATERS_CARDIGANS",
  "clip_men_T-SHIRTS",
  "clip_men_TROUSERS",
  "clip_SHIRTS",
  "clip_SHOES",
  "clip_WAISTCOATS_GILETS",
  "No Category"
];

function FashionAIChat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [image, setImage] = useState<string | undefined>(undefined);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("");

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/login", { state: { from: location.pathname } });
      return;
    }

    const checkToken = async () => {
      try {
        const response = await fetch("http://localhost:3001/auth/check", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          localStorage.removeItem("token");
          navigate("/login", { state: { from: location.pathname } });
        }
      } catch (error) {
        console.error("Token check error:", error);
        navigate("/login", { state: { from: location.pathname } });
      }
    };

    checkToken();
  }, []);

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
  // Utility to extract image URLs (full or partial)
  const extractImageUrls = (text: string): string[] => {
    const urls: string[] = [];

    // 1. Extract full image URLs that match the Zara image pattern
    const fullUrlRegex =
      /(https:\/\/static\.zara\.net\/photos\/[\/\w\d\-\._]+(\?ts=[0-9]+)?)\b/gi;

    // Match all full URLs in the text
    const matches = [...text.matchAll(fullUrlRegex)];
    matches.forEach((match) => urls.push(match[0]));

    return urls;
  };
  const removeImageUrlLine = (text: string): string => {
    // This regex matches any line that contains "**Image URL:**" (ignoring case)
    // and removes it along with the newline.
    return text.replace(/.*\*\*Image\s*URL:\*\*.*(?:\r?\n|$)/gi, "");
  };

  const handleMessage = async () => {
    if (!message.trim() && !image) return;

    // Directly add the user's message to the state
    setMessages((prev) => [
      ...prev,
      {
        text: message,
        sender: "user",
        imageBase64: image,
        category: selectedCategory, // Send selected category directly
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const email = localStorage.getItem("email");
      const botResponseText = await sendMessageToBackend(
        message,
        image,
        token,
        selectedCategory,
        email
      );
      // Extract image URLs from the bot's response text
      // Extract image URLs from the response text
      const extractedImageUrls = extractImageUrls(botResponseText);

      // First, remove any line that contains "**Image URL:**"
      let cleanText = removeImageUrlLine(botResponseText);

      // Then, remove any leftover image URLs (if any still exist in the text)
      cleanText = cleanText
        .replace(
          /https?:\/\/[^\s]+(?:\.(?:png|jpe?g|gif|webp))(\?ts=[^\s]*)?/gi,
          ""
        )
        .replace(/\s+/g, " ")
        .trim();
      console.log("After cleanup:", cleanText);

      // Add bot's response
      setMessages((prev) => [
        ...prev,
        {
          text: cleanText,
          sender: "bot",
          imageBase64: undefined,
          category: undefined,
          imageUrls: extractedImageUrls,
        },
      ]);
    } catch (error) {
      console.error("Error communicating with backend:", error);
      setMessages((prev) => [
        ...prev,
        {
          text: "Error: Unable to reach the server.",
          sender: "bot",
          imageBase64: undefined,
          category: undefined, // Error message doesn't need a category
        },
      ]);
    }

    setImage(undefined);
    setFilePreview(null);
    setFile(null);
    setLoading(false);
  };

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
      <Header />
      {/* Main Content */}
      <main className="fashion-chat-main">
        <h1 className="fashion-chat-title">Chat with me</h1>

        {/* Chat Messages */}
        <div className="fashion-chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`fashion-chat-message ${msg.sender}`}>
              <div className="fashion-chat-message-bubble">
                {/* Message Text */}
                {msg.text && <p>{msg.text}</p>}

                {/* User-uploaded image*/}
                {msg.imageBase64 && (
                  <img
                    src={msg.imageBase64}
                    alt="Uploaded"
                    className="fashion-chat-image"
                  />
                )}

                {/* Bot-sent image URLs */}
                {msg.imageUrls?.map((url, i) => (
                  <img
                    key={i}
                    src={url}
                    alt={`Bot suggestion ${i + 1}`}
                    className="fashion-chat-image"
                  />
                ))}
              </div>
            </div>
          ))}
          {loading && <p className="fashion-chat-loading">Thinking...</p>}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="fashion-chat-input-container">
          {/* Category Selection Dropdown */}
          <select
            className="fashion-chat-category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}>
            <option value="">Select Category</option>
            {valid_categories.map((category) => (
              <option key={category} value={category}>
                {category.replace("clip_", "").replace("_", " ")}
              </option>
            ))}
          </select>

          {/* Message Input */}
          <Input
            className="fashion-chat-input"
            placeholder="Type a message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
          />

          {filePreview && (
            <div className="fashion-chat-image-preview">
              <img
                src={filePreview}
                alt="Preview"
                className="fashion-chat-preview-image"
              />
            </div>
          )}

          {/* Action Buttons */}
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
