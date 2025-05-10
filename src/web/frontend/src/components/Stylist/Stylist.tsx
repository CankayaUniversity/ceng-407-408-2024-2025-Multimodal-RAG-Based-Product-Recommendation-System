import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../Header/Header";
import Button from "../ui/Button";
import { 
  Calendar, User, MessageSquare, Image, Clock, Send, 
  PlusCircle, Loader, CheckCircle, ChevronRight, ChevronDown 
} from "lucide-react";
import "./Stylist.css";

// Define consultation type interfaces
interface ConsultationQuestion {
  id: string;
  text: string;
}

interface FocusArea {
  id: string;
  name: string;
  description: string;
}

interface StylePreference {
  category: string;
  value: string;
}

interface Consultation {
  id: string;
  user_id: string;
  date: string;
  status: "scheduled" | "completed" | "cancelled";
  focus_areas: string[];
  questions: ConsultationQuestion[];
  style_preferences: StylePreference[];
  consultation_type: "ai" | "human";
  created_at: string;
  notes: ConsultationNote[];
  recommendations: ProductRecommendation[];
}

interface ConsultationNote {
  text: string;
  timestamp: string;
}

interface ProductRecommendation {
  product_id: string;
  product_name: string;
  reason: string;
  image_url: string | null;
  timestamp: string;
}

const Stylist: React.FC = () => {
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewConsultationForm, setShowNewConsultationForm] = useState(false);
  const [activeConsultation, setActiveConsultation] = useState<Consultation | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  // Available focus areas for consultations
  const focusAreas: FocusArea[] = [
    {
      id: "seasonal",
      name: "Seasonal Wardrobe",
      description: "Get advice on updating your wardrobe for the upcoming season"
    },
    {
      id: "occasion",
      name: "Special Occasion",
      description: "Find the perfect outfit for a special event"
    },
    {
      id: "colorAnalysis",
      name: "Color Analysis",
      description: "Discover which colors suit you best"
    },
    {
      id: "bodyType",
      name: "Body Type Styling",
      description: "Learn styles that flatter your body shape"
    },
    {
      id: "wardrobeEssentials",
      name: "Wardrobe Essentials",
      description: "Build a versatile capsule wardrobe"
    },
    {
      id: "trendAdaptation",
      name: "Trend Adaptation",
      description: "Incorporate current trends into your personal style"
    }
  ];

  // New consultation form state
  const [newConsultation, setNewConsultation] = useState({
    date: new Date().toISOString().split('T')[0],
    focus_areas: [] as string[],
    questions: [] as ConsultationQuestion[],
    style_preferences: [] as StylePreference[],
    consultation_type: "ai" as "ai" | "human"
  });
  
  // Quick question form state (for rapid AI advice)
  const [quickQuestion, setQuickQuestion] = useState("");
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [questionResponse, setQuestionResponse] = useState<string | null>(null);
  
  useEffect(() => {
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("email");
    
    if (!token) {
      navigate("/login", { state: { from: "/stylist" } });
      return;
    }
    
    if (email) {
      const name = email.split("@")[0];
      setUsername(name.charAt(0).toUpperCase() + name.slice(1));
    }

    // Fetch user's consultations
    const fetchConsultations = async () => {
      try {
        const response = await fetch("http://localhost:3001/api/stylist/consultations", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch consultations");
        }

        const data = await response.json();
        setConsultations(data.data || []);
        setLoading(false);
      } catch (err) {
        setError("Failed to load stylist consultations. Please try again later.");
        setLoading(false);
        console.error("Error fetching consultations:", err);
      }
    };

    fetchConsultations();
  }, [navigate]);

  // Handle toggling focus areas in new consultation form
  const toggleFocusArea = (areaId: string) => {
    const updatedFocusAreas = [...newConsultation.focus_areas];
    const index = updatedFocusAreas.indexOf(areaId);
    
    if (index === -1) {
      updatedFocusAreas.push(areaId);
    } else {
      updatedFocusAreas.splice(index, 1);
    }
    
    setNewConsultation({
      ...newConsultation,
      focus_areas: updatedFocusAreas
    });
  };

  // Add a question to the new consultation form
  const addQuestion = () => {
    const newQuestion: ConsultationQuestion = {
      id: `q_${Date.now()}`,
      text: ""
    };
    
    setNewConsultation({
      ...newConsultation,
      questions: [...newConsultation.questions, newQuestion]
    });
  };

  // Update a question in the new consultation form
  const updateQuestion = (id: string, text: string) => {
    const updatedQuestions = newConsultation.questions.map(q => 
      q.id === id ? { ...q, text } : q
    );
    
    setNewConsultation({
      ...newConsultation,
      questions: updatedQuestions
    });
  };

  // Remove a question from the new consultation form
  const removeQuestion = (id: string) => {
    const updatedQuestions = newConsultation.questions.filter(q => q.id !== id);
    
    setNewConsultation({
      ...newConsultation,
      questions: updatedQuestions
    });
  };

  // Submit the new consultation
  const submitConsultation = async () => {
    // Validate form
    if (newConsultation.focus_areas.length === 0) {
      alert("Please select at least one focus area");
      return;
    }
    
    // Filter out empty questions
    const validQuestions = newConsultation.questions.filter(q => q.text.trim() !== "");
    
    setIsSubmitting(true);
    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch("http://localhost:3001/api/stylist/consultations", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ...newConsultation,
          questions: validQuestions
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to create consultation");
      }
      
      const result = await response.json();
      
      // Add the new consultation to the list
      setConsultations([...consultations, result.data]);
      
      // Reset form and close it
      setNewConsultation({
        date: new Date().toISOString().split('T')[0],
        focus_areas: [],
        questions: [],
        style_preferences: [],
        consultation_type: "ai"
      });
      
      setShowNewConsultationForm(false);
      
    } catch (err) {
      console.error("Error creating consultation:", err);
      alert("Failed to schedule consultation. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Send a quick question to the AI stylist
  const askQuickQuestion = async () => {
    if (!quickQuestion.trim()) return;
    
    setAskingQuestion(true);
    setQuestionResponse(null);
    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch("http://localhost:3001/api/stylist/generate-advice", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: quickQuestion
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to get stylist advice");
      }
      
      const result = await response.json();
      setQuestionResponse(result.data.advice);
      
    } catch (err) {
      console.error("Error getting stylist advice:", err);
      setQuestionResponse("Sorry, I couldn't process your question at the moment. Please try again later.");
    } finally {
      setAskingQuestion(false);
    }
  };

  // View a consultation's details
  const viewConsultation = (consultation: Consultation) => {
    setActiveConsultation(consultation);
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="stylist-container">
      <Header />
      <main className="stylist-main">
        <section className="stylist-header">
          <div className="stylist-title">
            <h1>AI Fashion Stylist</h1>
            <p>Get personalized fashion advice and recommendations</p>
          </div>
          <div className="stylist-actions">
            <Button onClick={() => setShowNewConsultationForm(true)}>
              Schedule Consultation
            </Button>
          </div>
        </section>

        {/* Quick Question Section */}
        <section className="quick-question-section">
          <div className="quick-question-card">
            <h2><MessageSquare size={20} /> Ask the AI Stylist</h2>
            <p>Need quick fashion advice? Ask your question below:</p>
            
            <div className="quick-question-input">
              <input 
                type="text"
                placeholder="E.g., What colors go well with navy blue?"
                value={quickQuestion}
                onChange={(e) => setQuickQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && askQuickQuestion()}
                disabled={askingQuestion}
              />
              <button 
                className="send-question-button"
                onClick={askQuickQuestion}
                disabled={askingQuestion || !quickQuestion.trim()}
              >
                {askingQuestion ? <Loader size={18} className="spinning" /> : <Send size={18} />}
              </button>
            </div>
            
            {askingQuestion && (
              <div className="quick-question-loading">
                <Loader size={18} className="spinning" />
                <span>Processing your question...</span>
              </div>
            )}
            
            {questionResponse && (
              <div className="quick-question-response">
                <h3>Response:</h3>
                <p>{questionResponse}</p>
              </div>
            )}
          </div>
        </section>

        {/* Consultation Form */}
        {showNewConsultationForm && (
          <section className="consultation-form-section">
            <div className="consultation-form-card">
              <div className="form-card-header">
                <h2>Schedule New Consultation</h2>
                <button 
                  className="close-form-button"
                  onClick={() => setShowNewConsultationForm(false)}
                >
                  &times;
                </button>
              </div>
              
              <div className="consultation-form">
                <div className="form-group">
                  <label>Consultation Date</label>
                  <div className="date-input-group">
                    <Calendar size={18} />
                    <input 
                      type="date"
                      value={newConsultation.date}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={(e) => setNewConsultation({
                        ...newConsultation,
                        date: e.target.value
                      })}
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Focus Areas (Select at least one)</label>
                  <div className="focus-areas-grid">
                    {focusAreas.map(area => (
                      <div 
                        key={area.id}
                        className={`focus-area-item ${newConsultation.focus_areas.includes(area.id) ? 'selected' : ''}`}
                        onClick={() => toggleFocusArea(area.id)}
                      >
                        <div className="focus-area-checkbox">
                          {newConsultation.focus_areas.includes(area.id) && <CheckCircle size={16} />}
                        </div>
                        <div className="focus-area-content">
                          <h3>{area.name}</h3>
                          <p>{area.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Your Questions</label>
                  <p className="form-help-text">Add specific questions you'd like addressed during your consultation</p>
                  
                  {newConsultation.questions.map((question, index) => (
                    <div key={question.id} className="question-input-group">
                      <input 
                        type="text"
                        placeholder={`Question ${index + 1}`}
                        value={question.text}
                        onChange={(e) => updateQuestion(question.id, e.target.value)}
                      />
                      <button 
                        className="remove-question-button"
                        onClick={() => removeQuestion(question.id)}
                      >
                        &times;
                      </button>
                    </div>
                  ))}
                  
                  <button 
                    className="add-question-button"
                    onClick={addQuestion}
                  >
                    <PlusCircle size={16} />
                    Add Question
                  </button>
                </div>
                
                <div className="form-group">
                  <label>Consultation Type</label>
                  <div className="radio-group">
                    <div className="radio-option">
                      <input 
                        type="radio"
                        id="ai-consultation"
                        name="consultation-type"
                        checked={newConsultation.consultation_type === "ai"}
                        onChange={() => setNewConsultation({
                          ...newConsultation,
                          consultation_type: "ai"
                        })}
                      />
                      <label htmlFor="ai-consultation">AI Stylist (Immediate)</label>
                    </div>
                    <div className="radio-option">
                      <input 
                        type="radio"
                        id="human-consultation"
                        name="consultation-type"
                        checked={newConsultation.consultation_type === "human"}
                        onChange={() => setNewConsultation({
                          ...newConsultation,
                          consultation_type: "human"
                        })}
                      />
                      <label htmlFor="human-consultation">Human Stylist (Scheduled)</label>
                    </div>
                  </div>
                </div>
                
                <div className="form-actions">
                  <button 
                    className="cancel-button"
                    onClick={() => setShowNewConsultationForm(false)}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </button>
                  <button 
                    className="submit-button"
                    onClick={submitConsultation}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <Loader size={16} className="spinning" />
                        Scheduling...
                      </>
                    ) : (
                      <>Schedule Consultation</>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Consultations List */}
        <section className="consultations-section">
          <h2>Your Consultations</h2>
          
          {loading ? (
            <div className="consultations-loading">
              <Loader size={24} className="spinning" />
              <p>Loading your consultations...</p>
            </div>
          ) : error ? (
            <div className="consultations-error">
              <p>{error}</p>
              <Button onClick={() => window.location.reload()}>Try Again</Button>
            </div>
          ) : consultations.length === 0 ? (
            <div className="no-consultations">
              <p>You don't have any consultations yet.</p>
              <Button onClick={() => setShowNewConsultationForm(true)}>Schedule Your First Consultation</Button>
            </div>
          ) : (
            <div className="consultations-list">
              {consultations.map(consultation => (
                <div key={consultation.id} className="consultation-card">
                  <div className="consultation-card-header">
                    <div className="consultation-type">
                      {consultation.consultation_type === "ai" ? (
                        <span className="ai-badge">AI Stylist</span>
                      ) : (
                        <span className="human-badge">Human Stylist</span>
                      )}
                      <span className={`status-badge ${consultation.status}`}>{consultation.status}</span>
                    </div>
                    <div className="consultation-date">
                      <Clock size={16} />
                      {formatDate(consultation.date)}
                    </div>
                  </div>
                  
                  <div className="consultation-focus-areas">
                    <h3>Focus Areas:</h3>
                    <div className="focus-tags">
                      {consultation.focus_areas.map(area => {
                        const focusArea = focusAreas.find(a => a.id === area);
                        return (
                          <span key={area} className="focus-tag">
                            {focusArea ? focusArea.name : area}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                  
                  {consultation.questions.length > 0 && (
                    <div className="consultation-questions">
                      <h3>Questions:</h3>
                      <ul>
                        {consultation.questions.slice(0, 2).map(question => (
                          <li key={question.id}>{question.text}</li>
                        ))}
                        {consultation.questions.length > 2 && (
                          <li className="more-questions">
                            +{consultation.questions.length - 2} more questions
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                  
                  {consultation.recommendations && consultation.recommendations.length > 0 && (
                    <div className="consultation-recommendations-preview">
                      <h3>Recommendations:</h3>
                      <div className="recommendation-count">
                        {consultation.recommendations.length} product recommendations
                      </div>
                    </div>
                  )}
                  
                  <button 
                    className="view-consultation-button"
                    onClick={() => viewConsultation(consultation)}
                  >
                    View Details
                    <ChevronRight size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Active Consultation Details */}
        {activeConsultation && (
          <div className="consultation-details-overlay">
            <div className="consultation-details-modal">
              <div className="modal-header">
                <h2>Consultation Details</h2>
                <button 
                  className="close-modal-button"
                  onClick={() => setActiveConsultation(null)}
                >
                  &times;
                </button>
              </div>
              
              <div className="modal-content">
                <div className="consultation-info">
                  <div className="consultation-info-header">
                    <div>
                      <span className={`type-badge ${activeConsultation.consultation_type}`}>
                        {activeConsultation.consultation_type === "ai" ? "AI Stylist" : "Human Stylist"}
                      </span>
                      <span className={`status-badge ${activeConsultation.status}`}>
                        {activeConsultation.status}
                      </span>
                    </div>
                    <div className="info-date">
                      <Calendar size={16} />
                      {formatDate(activeConsultation.date)}
                    </div>
                  </div>
                  
                  <div className="info-section">
                    <h3>Focus Areas</h3>
                    <div className="focus-tags">
                      {activeConsultation.focus_areas.map(area => {
                        const focusArea = focusAreas.find(a => a.id === area);
                        return (
                          <span key={area} className="focus-tag">
                            {focusArea ? focusArea.name : area}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                  
                  {activeConsultation.questions.length > 0 && (
                    <div className="info-section">
                      <h3>Your Questions</h3>
                      <ul className="questions-list">
                        {activeConsultation.questions.map(question => (
                          <li key={question.id}>{question.text}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {activeConsultation.notes && activeConsultation.notes.length > 0 && (
                    <div className="info-section">
                      <h3>Stylist Notes</h3>
                      <div className="notes-list">
                        {activeConsultation.notes.map((note, index) => (
                          <div key={index} className="note-item">
                            <p>{note.text}</p>
                            <div className="note-timestamp">
                              {formatDate(note.timestamp)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {activeConsultation.recommendations && activeConsultation.recommendations.length > 0 && (
                    <div className="info-section recommendations-section">
                      <h3>Recommendations</h3>
                      <div className="recommendations-grid">
                        {activeConsultation.recommendations.map((rec, index) => (
                          <div key={index} className="recommendation-card">
                            {rec.image_url && (
                              <div className="recommendation-image">
                                <img 
                                  src={rec.image_url} 
                                  alt={rec.product_name}
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).src = "https://placehold.co/300x300?text=Product";
                                  }}
                                />
                              </div>
                            )}
                            <div className="recommendation-info">
                              <h4>{rec.product_name}</h4>
                              <p>{rec.reason}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="modal-footer">
                <button 
                  className="close-button"
                  onClick={() => setActiveConsultation(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Stylist; 