import { useState, useEffect, useRef } from "react";
import { Paperclip, Send, Shirt } from "lucide-react";
import Avatar from "../ui/Avatar";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Header from "../Header/Header";
import "./FashionChat.css";
import { useNavigate } from "react-router-dom";
import { Message } from "../../types/message";
import { sendMessageToBackend } from "../../api/ChatService";
import TextareaAutosize from "react-textarea-autosize";

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
  "No Category",
];

// Add this interface for try-on state
interface TryOnState {
  isOpen: boolean;
  imageUrl: string | null;
  productName: string | null;
  userPhoto: string | null;
}

function FashionAIChat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [image, setImage] = useState<string | undefined>(undefined);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] =
    useState<string>("No Category");
  
  // Updated Try-On state with userPhoto field
  const [tryOnModal, setTryOnModal] = useState<TryOnState>({
    isOpen: false,
    imageUrl: null,
    productName: null,
    userPhoto: null
  });

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const tryOnFileInputRef = useRef<HTMLInputElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
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
        } else {
          // Add welcome message when the chat loads
          const username = localStorage.getItem("email")?.split("@")[0] || "there";
          setMessages([
            {
              text: `Hello ${username}! I'm your fashion assistant. How can I help with your style needs today? You can ask for outfit suggestions, search for specific products, or upload a photo to find similar items.`,
              sender: "bot",
              imageBase64: undefined,
              category: undefined,
              imageUrls: []
            }
          ]);
        }
      } catch (error) {
        console.error("Token check error:", error);
        navigate("/login", { state: { from: location.pathname } });
      }
    };

    checkToken();
    
    // Focus the input field on load
    setTimeout(() => {
      inputRef.current?.focus();
    }, 500);
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

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // prevent default newline
      handleMessage(); // send the message
    }
  };

  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  // Clear the chat history
  const clearChat = () => {
    const username = localStorage.getItem("email")?.split("@")[0] || "there";
    setMessages([
      {
        text: `Hello ${username}! I'm your fashion assistant. How can I help with your style needs today?`,
        sender: "bot",
        imageBase64: undefined,
        category: undefined,
        imageUrls: []
      }
    ]);
  };

  // Handle Try On button click
  const handleTryOn = (imageUrl: string, productName: string) => {
    setTryOnModal({
      isOpen: true,
      imageUrl,
      productName,
      userPhoto: null
    });
  };

  // Close try-on modal
  const closeTryOnModal = () => {
    setTryOnModal({
      ...tryOnModal,
      isOpen: false
    });
  };

  // Handle user photo upload for try-on
  const handleTryOnPhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setTryOnModal({
          ...tryOnModal,
          userPhoto: reader.result as string
        });
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  // Trigger try-on photo upload
  const triggerTryOnPhotoUpload = () => {
    tryOnFileInputRef.current?.click();
  };

  // Adjust fit position - this could be expanded with more advanced positioning controls
  const adjustFit = () => {
    // This would be implemented with more advanced positioning logic
    alert("Fit adjustment feature will be available soon!");
  };

  return (
    <div className="fashion-chat-container">
      <Header />
      {/* Main Content */}
      <main className="fashion-chat-main">
        <div className="fashion-chat-header-controls">
          <h1 className="fashion-chat-title">Fashion Assistant</h1>
          <button onClick={clearChat} className="fashion-chat-clear-button">
            Clear Chat
          </button>
        </div>

        {/* Chat Messages */}
        <div className="fashion-chat-messages">
          {messages.length === 0 && !loading && (
            <div className="fashion-chat-empty-state">
              <div className="fashion-chat-empty-icon">💬</div>
              <p>Send a message to start your fashion conversation</p>
            </div>
          )}
        
          {messages.map((msg, index) => (
            <div key={index} className={`fashion-chat-message ${msg.sender}`}>
              {msg.sender === "bot" && (
                <div className="fashion-chat-avatar">
                  <div className="fashion-chat-avatar-icon">AI</div>
                </div>
              )}
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

                {/* Bot-sent image URLs with Try On button */}
                {msg.sender === "bot" && msg.imageUrls && msg.imageUrls.length > 0 && (
                  <div className="fashion-chat-product-grid">
                    {msg.imageUrls.map((url, i) => (
                      <div key={i} className="fashion-chat-product-container">
                        <img
                          src={url}
                          alt={`Bot suggestion ${i + 1}`}
                          className="fashion-chat-image"
                          loading="lazy"
                        />
                        <Button 
                          onClick={() => handleTryOn(url, `Product ${i + 1}`)}
                          className="fashion-chat-try-on-button"
                        >
                          <Shirt size={16} />
                          Try On
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {msg.sender === "user" && (
                <div className="fashion-chat-avatar user">
                  <div className="fashion-chat-avatar-icon">You</div>
                </div>
              )}
            </div>
          ))}
          {loading && <div className="fashion-chat-loading">Thinking</div>}
          <div ref={messagesEndRef} />
        </div>

        {/* Try On Modal */}
        {tryOnModal.isOpen && (
          <div className="fashion-try-on-modal-overlay">
            <div className="fashion-try-on-modal">
              <div className="fashion-try-on-modal-header">
                <h2>Virtual Try On</h2>
                <button 
                  className="fashion-try-on-close-button"
                  onClick={closeTryOnModal}
                >
                  ×
                </button>
              </div>
              <div className="fashion-try-on-modal-content">
                <div className="fashion-try-on-product">
                  <img 
                    src={tryOnModal.imageUrl || ''} 
                    alt={tryOnModal.productName || 'Product'} 
                  />
                  <p>{tryOnModal.productName}</p>
                </div>
                <div className="fashion-try-on-preview">
                  <div className="fashion-try-on-avatar">
                    {tryOnModal.userPhoto ? (
                      <img 
                        src={tryOnModal.userPhoto} 
                        alt="User Avatar" 
                        className="fashion-try-on-avatar-image" 
                      />
                    ) : (
                      <div className="fashion-try-on-upload-prompt">
                        <div className="fashion-try-on-upload-icon">
                          <Paperclip size={24} />
                        </div>
                        <p>Upload your photo to see how this would look on you</p>
                      </div>
                    )}
                    {tryOnModal.imageUrl && tryOnModal.userPhoto && (
                      <img 
                        src={tryOnModal.imageUrl} 
                        alt="Overlaid product" 
                        className="fashion-try-on-overlay-image" 
                      />
                    )}
                  </div>
                  <div className="fashion-try-on-controls">
                    <Button 
                      className="fashion-try-on-control-button"
                      onClick={triggerTryOnPhotoUpload}
                    >
                      Upload Your Photo
                    </Button>
                    <Button 
                      className="fashion-try-on-control-button"
                      onClick={adjustFit}
                      disabled={!tryOnModal.userPhoto}
                    >
                      Adjust Fit
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="fashion-chat-input-container">
          {/* Chat Input Row */}
          <div className="fashion-chat-input-row">
            {/* Category Dropdown */}
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

            {/* Growing Textarea */}
            <TextareaAutosize
              ref={inputRef}
              className="fashion-chat-input"
              placeholder="Type a message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              minRows={1}
              maxRows={5}
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
            {/* Attachment and Send Buttons */}
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
                <Send size={20} className="fashion-chat-send-icon" />
              </Button>
            </div>
          </div>
        </div>
      </main>

      {/* Hidden File Inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      <input
        ref={tryOnFileInputRef}
        type="file"
        accept="image/*"
        onChange={handleTryOnPhotoUpload}
        style={{ display: "none" }}
      />
    </div>
  );
}

export default FashionAIChat;
