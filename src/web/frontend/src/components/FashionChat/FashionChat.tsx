import { useState, useEffect, useRef } from "react";
import { Paperclip, Send, Shirt, Loader, X, RotateCcw } from "lucide-react";
import Avatar from "../ui/Avatar";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Header from "../Header/Header";
import "./FashionChat.css";
import { useNavigate } from "react-router-dom";
import { Message } from "../../types/message";
import { sendMessageToBackend } from "../../api/ChatService";
import TextareaAutosize from "react-textarea-autosize";
import ReactMarkdown from 'react-markdown';

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
  "beymen_women_dresses",
  "beymen_women_jackets",
  "beymen_women_skirts",
  "beymen_women_sweatshirts",
  "No Category",
];

// Add this interface for try-on state
interface TryOnState {
  isOpen: boolean;
  imageUrl: string | null;
  productName: string | null;
  userPhoto: string | null;
  resultImage: string | null;
  isLoading: boolean;
  error: string | null;
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
  
  // Updated Try-On state with resultImage, isLoading, and error fields
  const [tryOnModal, setTryOnModal] = useState<TryOnState>({
    isOpen: false,
    imageUrl: null,
    productName: null,
    userPhoto: null,
    resultImage: null,
    isLoading: false,
    error: null
  });

  // Add new state for tracking image load status
  const [imageLoadStatus, setImageLoadStatus] = useState<Record<string, boolean>>({});
  const imageRefs = useRef<Record<string, HTMLImageElement | null>>({});

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
          console.error("Token validation failed:", response.status);
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
          
          // Set up periodic token check (every 5 minutes)
          const tokenCheckInterval = setInterval(() => {
            const currentToken = localStorage.getItem("token");
            if (currentToken) {
              fetch("http://localhost:3001/auth/check", {
                method: "GET",
                headers: {
                  Authorization: `Bearer ${currentToken}`,
                },
              }).then(response => {
                if (!response.ok) {
                  console.warn("Token expired during session");
                  clearInterval(tokenCheckInterval);
                  localStorage.removeItem("token");
                  setMessages(prev => [
                    ...prev,
                    {
                      text: "Your session has expired. Please log in again to continue.",
                      sender: "bot",
                      imageBase64: undefined,
                      category: undefined,
                    }
                  ]);
                  // Give user a moment to read the message before redirecting
                  setTimeout(() => {
                    navigate("/login", { state: { from: location.pathname } });
                  }, 3000);
                }
              }).catch(err => {
                console.error("Token check error:", err);
              });
            } else {
              clearInterval(tokenCheckInterval);
            }
          }, 5 * 60 * 1000); // Check every 5 minutes
          
          // Clear interval on component unmount
          return () => clearInterval(tokenCheckInterval);
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

  // Utility to clean up image URLs
  const cleanImageUrl = (url: string): string => {
    // Handle Zara URLs specifically
    if (url.includes('zara.net')) {
      // Replace multiple consecutive slashes with a single slash
      let cleanedUrl = url.replace(/([^:]\/)\/+/g, '$1');
      
      // Fix protocol handling
      if (cleanedUrl.includes('://')) {
        const [protocol, rest] = cleanedUrl.split('://', 2);
        cleanedUrl = `${protocol}://${rest.replace(/\/+/g, '/')}`;
      }
      
      return cleanedUrl;
    }
    return url;
  };

  // Utility to extract image URLs (full or partial)
  const extractImageUrls = (text: string): string[] => {
    const urls: string[] = [];

    // Log the incoming text for debugging
    console.log('Extracting URLs from text:', text);

    // 1. Extract full image URLs that match the Zara image pattern
    const zaraUrlRegex = /(https:\/\/static\.zara\.net\/photos\/[\/\w\d\-\._]+(\?ts=[0-9]+)?)\b/gi;
    
    // 2. Extract any other image URLs
    const generalUrlRegex = /(https?:\/\/[^\s]+(?:\.(?:png|jpe?g|gif|webp))(\?[^\s]*)?)\b/gi;

    // Match all Zara URLs in the text
    const zaraMatches = [...text.matchAll(zaraUrlRegex)];
    zaraMatches.forEach((match) => {
      const cleanedUrl = cleanImageUrl(match[0]);
      urls.push(cleanedUrl);
    });

    // Match all other image URLs in the text
    const generalMatches = [...text.matchAll(generalUrlRegex)];
    generalMatches.forEach((match) => {
      const cleanedUrl = cleanImageUrl(match[0]);
      // Only add if it's not already in the urls array
      if (!urls.includes(cleanedUrl)) {
        urls.push(cleanedUrl);
      }
    });

    // Log the extracted URLs for debugging
    console.log('Extracted URLs:', urls);

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
        category: selectedCategory,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("You must be logged in to use the chat service");
      }
      
      const email = localStorage.getItem("email");
      
      // First check if the token is still valid
      try {
        const tokenCheckResponse = await fetch("http://localhost:3001/auth/check", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        
        if (!tokenCheckResponse.ok) {
          localStorage.removeItem("token");
          throw new Error("Your session has expired. Please log in again.");
        }
      } catch (tokenError) {
        console.error("Token validation error:", tokenError);
        throw new Error("Authentication error. Please log in again.");
      }
      
      console.log('Sending message to backend:', { message, category: selectedCategory });
      const botResponseText = await sendMessageToBackend(
        message,
        image,
        token,
        selectedCategory,
        email
      );
      
      console.log('Received response from backend:', botResponseText);
      
      // Extract image URLs from the bot's response text
      const extractedImageUrls = extractImageUrls(botResponseText);
      console.log('Extracted image URLs:', extractedImageUrls);

      // Extract product links (not image URLs)
      const linkRegex = /(https?:\/\/(?!static\.|cdn\.|placehold\.co)[^\s]+(?:\/[^\s]*)?)/gi;
      const allLinks = [...botResponseText.matchAll(linkRegex)].map(match => match[0]);
      
      // Extract links labeled with "Link:" pattern - these are most likely product links
      const labeledLinkRegex = /Link:\s*(https?:\/\/[^\s,]+)/gi;
      const labeledLinks = [...botResponseText.matchAll(labeledLinkRegex)].map(match => match[1]);
      
      // Extract links following 'Product:' that aren't image URLs - these are often product links
      const productLinkRegex = /Product:.*?(https?:\/\/(?!.*\.(jpg|jpeg|png|gif|webp))[^\s,]+)/gi;
      const productLinks = [...botResponseText.matchAll(productLinkRegex)].map(match => match[1]);
      
      // Combine all links, prioritizing labeled links first
      const combinedLinks = [...labeledLinks, ...productLinks, ...allLinks];
      
      // Filter out image links and duplicates
      const uniqueProductLinks = Array.from(new Set(
        combinedLinks.filter(link => 
          !link.match(/\.(jpg|jpeg|png|webp|gif)$/i) && 
          !link.includes('static.zara.net') &&
          !link.includes('placehold.co')
        )
      ));
      
      console.log('Extracted product links:', uniqueProductLinks);

      // First, remove any line that contains "**Image URL:**"
      let cleanText = removeImageUrlLine(botResponseText);

      // Then, remove any leftover image URLs (if any still exist in the text)
      cleanText = cleanText
        .replace(
          /https?:\/\/[^\s]+(?:\.(?:png|jpe?g|gif|webp))(\?[^\s]*)?/gi,
          ""
        )
        .replace(/\s+/g, " ")
        .trim();
      
      console.log('Cleaned text:', cleanText);

      // Add bot's response
      setMessages((prev) => [
        ...prev,
        {
          text: cleanText,
          sender: "bot",
          imageBase64: undefined,
          category: undefined,
          imageUrls: extractedImageUrls,
          links: uniqueProductLinks,
        },
      ]);
    } catch (error) {
      console.error("Error in handleMessage:", error);
      
      let errorMessage = "Error: Unable to reach the server.";
      
      if (error instanceof Error) {
        if (error.message.includes("session has expired") || 
            error.message.includes("log in again")) {
          errorMessage = error.message;
          setTimeout(() => {
            navigate("/login", { state: { from: location.pathname } });
          }, 3000);
        } else {
          errorMessage = `Error: ${error.message}`;
        }
      }
      
      setMessages((prev) => [
        ...prev,
        {
          text: errorMessage,
          sender: "bot",
          imageBase64: undefined,
          category: undefined,
          imageUrls: [],
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
    // Ensure URL is properly encoded, especially for Zara URLs with multiple slashes
    let processedUrl = imageUrl;
    
    // Reset the modal state completely
    setTryOnModal({
      isOpen: true,
      imageUrl: processedUrl,
      productName,
      userPhoto: null,
      resultImage: null,
      isLoading: false,
      error: null
    });
    
    // Reset the file input
    if (tryOnFileInputRef.current) {
      tryOnFileInputRef.current.value = '';
    }
  };

  // Reset try-on process
  const resetTryOn = () => {
    setTryOnModal({
      ...tryOnModal,
      userPhoto: null,
      resultImage: null,
      error: null
    });
    
    // Reset the file input element so the same file can be selected again
    if (tryOnFileInputRef.current) {
      tryOnFileInputRef.current.value = '';
    }
  };

  // Close try-on modal with full reset
  const closeTryOnModal = () => {
    setTryOnModal({
      isOpen: false,
      imageUrl: null,
      productName: null,
      userPhoto: null,
      resultImage: null,
      isLoading: false,
      error: null
    });
    
    // Reset the file input element when closing the modal
    if (tryOnFileInputRef.current) {
      tryOnFileInputRef.current.value = '';
    }
  };

  // Handle user photo upload for try-on
  const handleTryOnPhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setTryOnModal({
          ...tryOnModal,
          userPhoto: reader.result as string,
          resultImage: null, // Clear previous result
          error: null // Clear any previous errors
        });
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  // Trigger try-on photo upload
  const triggerTryOnPhotoUpload = () => {
    // Reset the file input value first, so the same file can be selected again
    if (tryOnFileInputRef.current) {
      tryOnFileInputRef.current.value = '';
    }
    tryOnFileInputRef.current?.click();
  };

  // Process try-on with uploaded image
  const processTryOn = async () => {
    if (!tryOnModal.userPhoto || !tryOnModal.imageUrl) {
      setTryOnModal({
        ...tryOnModal,
        error: "Both your photo and a clothing item are required"
      });
      return;
    }
    
    setTryOnModal({
      ...tryOnModal,
      isLoading: true,
      error: null
    });
    
    try {
      console.log("Starting try-on process");
      
      // Create a FormData object to send the image URLs
      const formData = new FormData();
      formData.append('avatar_image_url', tryOnModal.userPhoto);
      formData.append('clothing_image_url', tryOnModal.imageUrl);
      
      console.log("Sending request to try-on API");
      
      // Send request to our backend API with a timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
      
      const response = await fetch('http://localhost:3001/api/tryon', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        console.error("Try-on API error:", response.status, response.statusText);
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to process try-on request (Status: ${response.status})`);
      }
      
      const result = await response.json();
      
      console.log("Try-on response received:", result);
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      if (!result.image) {
        throw new Error("No image was returned from the server");
      }
      
      // Update state with the result image
      setTryOnModal({
        ...tryOnModal,
        resultImage: `data:${result.content_type || 'image/png'};base64,${result.image}`,
        isLoading: false
      });
      
    } catch (error) {
      console.error('Try-on processing error:', error);
      setTryOnModal({
        ...tryOnModal,
        error: error instanceof Error ? error.message : 'An unknown error occurred during processing',
        isLoading: false
      });
      
      // Add a retry option if it was a timeout or network error
      if (
        error instanceof DOMException || 
        (error && typeof error === 'object' && 'name' in error && error.name === 'AbortError')
      ) {
        setTryOnModal(prev => ({
          ...prev, 
          error: 'Request timed out. The server may be busy. Please try again.'
        }));
      }
    }
  };

  // Add function to handle image load status
  const handleImageLoadStatus = (url: string, hasError: boolean) => {
    console.log(`Image load status for ${url}:`, !hasError);
    setImageLoadStatus(prev => {
      const newStatus = {
        ...prev,
        [url]: !hasError
      };
      console.log('Updated image load status:', newStatus);
      return newStatus;
    });
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
                {/* Message Text - Updated to use Markdown for bot messages */}
                {msg.text && msg.sender === "bot" ? (
                  <div className="markdown-content">
                    <ReactMarkdown
                      children={msg.text}
                      components={{
                        strong: ({ node, ...props }) => {
                          // Special handling for Reasoning: and Product: labels
                          const content = props.children?.toString() || '';
                          if (content.startsWith('Reasoning:') || content.startsWith('Product:')) {
                            return <strong className="section-header" {...props} />;
                          }
                          return <strong {...props} />;
                        },
                        p: ({ node, ...props }) => {
                          // Apply special styling to paragraphs containing section headers
                          const content = props.children?.toString() || '';
                          if (
                            content.includes('Reasoning:') || 
                            content.includes('Product:')
                          ) {
                            return <p className="section-paragraph" {...props} />;
                          }
                          return <p {...props} />;
                        }
                      }}
                    />
                  </div>
                ) : (
                  <p>{msg.text}</p>
                )}

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
                    {msg.imageUrls.map((url, i) => {
                      console.log(`Rendering image ${i + 1} with URL:`, url);
                      console.log('Current load status:', imageLoadStatus[url]);
                      return (
                        <div key={i} className="fashion-chat-product-container">
                          <img
                            ref={(el) => {
                              if (el) {
                                imageRefs.current[url] = el;
                              }
                            }}
                            src={url}
                            alt={`Bot suggestion ${i + 1}`}
                            className="fashion-chat-image"
                            loading="lazy"
                            onError={(e) => {
                              console.log(`Image load error for ${url}`);
                              const placeholderUrl = "https://placehold.co/400x600?text=Product+Image+Not+Available";
                              // Replace with a fallback image when the original fails to load
                              e.currentTarget.src = placeholderUrl;
                              // Log the error for debugging
                              console.error(`Failed to load image from URL: ${url}`);
                              // Add a class to indicate the image failed to load
                              e.currentTarget.classList.add('image-load-error');
                              // Update load status for both original and placeholder URLs
                              handleImageLoadStatus(url, true);
                              handleImageLoadStatus(placeholderUrl, true);
                            }}
                            onLoad={(e) => {
                              console.log(`Image loaded successfully for ${url}`);
                              // Remove error class if the image loads successfully
                              e.currentTarget.classList.remove('image-load-error');
                              // Only update load status if it's not a placeholder image
                              if (!url.includes('placehold.co')) {
                                handleImageLoadStatus(url, false);
                              }
                            }}
                          />
                          {/* Always show buttons for product recommendations */}
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            position: 'absolute',
                            bottom: '12px',
                            left: '12px',
                            right: '12px',
                            width: 'calc(100% - 24px)',
                            zIndex: 10
                          }}>
                            {/* Buy button on the left */}
                            {msg.links && msg.links[i] && !msg.links[i].includes('.jpg') && !msg.links[i].includes('.png') ? (
                              <a 
                                href={msg.links[i]} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                style={{ textDecoration: 'none' }}
                              >
                                <Button className="fashion-chat-buy-button">
                                  Buy
                                </Button>
                              </a>
                            ) : (
                              <Button 
                                className="fashion-chat-buy-button-disabled"
                                disabled={true}
                              >
                                Buy
                              </Button>
                            )}
                            
                            {/* Try On button on the right */}
                            <Button 
                              onClick={() => handleTryOn(url, `Product ${i + 1}`)}
                              className="fashion-chat-try-on-button"
                            >
                              <Shirt size={16} />
                              Try On
                            </Button>
                          </div>
                        </div>
                      );
                    })}
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
                  <X size={20} />
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
                  {tryOnModal.resultImage ? (
                    <div className="fashion-try-on-result">
                      <img 
                        src={tryOnModal.resultImage}
                        alt="Try-on result" 
                        className="fashion-try-on-result-image"
                      />
                      <div className="fashion-try-on-controls">
                        <Button 
                          className="fashion-try-on-control-button"
                          onClick={resetTryOn}
                        >
                          <RotateCcw size={18} />
                          Try Different Photo
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
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
                      </div>
                      <div className="fashion-try-on-controls">
                        <Button 
                          className="fashion-try-on-control-button"
                          onClick={triggerTryOnPhotoUpload}
                        >
                          {tryOnModal.userPhoto ? 'Choose Different Photo' : 'Upload Your Photo'}
                        </Button>
                        <Button 
                          className="fashion-try-on-control-button try-on-process-button"
                          onClick={processTryOn}
                          disabled={!tryOnModal.userPhoto || tryOnModal.isLoading}
                        >
                          {tryOnModal.isLoading ? (
                            <>
                              <Loader size={18} className="spinning" />
                              Processing...
                            </>
                          ) : (
                            <>
                              <Shirt size={18} />
                              Generate Try-On
                            </>
                          )}
                        </Button>
                      </div>
                    </>
                  )}
                  
                  {/* Error message */}
                  {tryOnModal.error && (
                    <div className="fashion-try-on-error">
                      <p>{tryOnModal.error}</p>
                    </div>
                  )}
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
