import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../Header/Header';
import { 
  User, 
  Calendar, 
  Clock, 
  Send, 
  MessageSquare, 
  CalendarClock, 
  History, 
  HelpCircle, 
  ChevronRight, 
  Loader, 
  Image, 
  AlignLeft
} from 'lucide-react';
import './AIStylist.css';

interface StylistConsultation {
  id: string;
  title: string;
  dateTime: string;
  status: 'scheduled' | 'completed' | 'cancelled';
  duration: number;
  stylistName: string;
  notes?: string;
}

interface QuickQuestion {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
}

interface Recommendation {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  items: RecommendedItem[];
}

interface RecommendedItem {
  id: string;
  name: string;
  image: string;
  price: number;
  url: string;
}

const AIStylist: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'consultations' | 'questions' | 'recommendations'>('consultations');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [consultations, setConsultations] = useState<StylistConsultation[]>([]);
  const [questions, setQuestions] = useState<QuickQuestion[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [newConsultationModal, setNewConsultationModal] = useState(false);
  const [newConsultation, setNewConsultation] = useState({
    date: '',
    time: '',
    duration: 30,
    notes: ''
  });

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login', { state: { from: '/stylist' } });
      return;
    }
    
    fetchStylistData();
  }, [navigate]);

  const fetchStylistData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, these would be API calls
      // For now, use mock data with a setTimeout to simulate loading
      setTimeout(() => {
        // Mock consultations
        const mockConsultations: StylistConsultation[] = [
          {
            id: 'cons-1',
            title: 'Summer Wardrobe Planning',
            dateTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days from now
            status: 'scheduled',
            duration: 30,
            stylistName: 'Emma Rodriguez'
          },
          {
            id: 'cons-2',
            title: 'Workplace Style Consultation',
            dateTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
            status: 'completed',
            duration: 45,
            stylistName: 'Michael Chen',
            notes: 'Focused on business casual attire for tech industry. Recommendations for versatile pieces sent.'
          }
        ];
        
        // Mock quick questions
        const mockQuestions: QuickQuestion[] = [
          {
            id: 'q-1',
            question: 'How do I style a white button-down shirt for different occasions?',
            answer: 'A white button-down is incredibly versatile! For casual looks, try it with jeans and sneakers or tucked into a midi skirt. For work, pair with tailored pants or a pencil skirt. For evening, try it half-tucked into black jeans with statement jewelry and heels. You can also layer under sweaters or blazers for added dimension.',
            timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() // 2 days ago
          },
          {
            id: 'q-2',
            question: 'What colors would look best with my warm skin tone?',
            answer: 'For warm skin tones, earthy colors like olive green, coral, cream, amber, and gold typically look fantastic. Also consider warm reds, peachy pinks, and yellow-based blues like teal. These will complement your natural coloring and make your complexion glow. Try to avoid harsh colors like stark white, icy blues, or fuchsia pink.',
            timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString() // 10 days ago
          }
        ];
        
        // Mock recommendations
        const mockRecommendations: Recommendation[] = [
          {
            id: 'rec-1',
            title: 'Fall Capsule Wardrobe Essentials',
            description: 'Based on your style profile and preferences, here are key pieces to create a versatile fall wardrobe that works with your business casual needs.',
            timestamp: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days ago
            items: [
              {
                id: 'item-1',
                name: 'Camel Trench Coat',
                image: 'https://via.placeholder.com/150?text=Trench+Coat',
                price: 129.99,
                url: '#'
              },
              {
                id: 'item-2',
                name: 'Navy Merino Wool Sweater',
                image: 'https://via.placeholder.com/150?text=Wool+Sweater',
                price: 79.99,
                url: '#'
              },
              {
                id: 'item-3',
                name: 'Dark Wash Straight Leg Jeans',
                image: 'https://via.placeholder.com/150?text=Jeans',
                price: 89.99,
                url: '#'
              }
            ]
          },
          {
            id: 'rec-2',
            title: 'Weekend Outfit Combinations',
            description: 'Mix and match these casual pieces for effortless weekend style that aligns with your personal aesthetic.',
            timestamp: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(), // 21 days ago
            items: [
              {
                id: 'item-4',
                name: 'White Sneakers',
                image: 'https://via.placeholder.com/150?text=Sneakers',
                price: 69.99,
                url: '#'
              },
              {
                id: 'item-5',
                name: 'Striped Boatneck Tee',
                image: 'https://via.placeholder.com/150?text=Striped+Tee',
                price: 29.99,
                url: '#'
              },
              {
                id: 'item-6',
                name: 'Denim Jacket',
                image: 'https://via.placeholder.com/150?text=Denim+Jacket',
                price: 79.99,
                url: '#'
              }
            ]
          }
        ];
        
        setConsultations(mockConsultations);
        setQuestions(mockQuestions);
        setRecommendations(mockRecommendations);
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError('Failed to load stylist data. Please try again.');
      setLoading(false);
    }
  };

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newQuestion.trim()) return;
    
    setAskingQuestion(true);
    
    try {
      // In a real app, this would be an API call to send the question to the AI
      // For now, simulate a delay and create a mock response
      setTimeout(() => {
        const mockAnswer = "That's a great question! Based on current trends and your style profile, I'd recommend pairing your new jeans with a relaxed-fit blazer and a simple tee for a casual but put-together look. Ankle boots or white sneakers would complete the outfit perfectly. Let me know if you'd like more specific suggestions!";
        
        const newQuestionObj: QuickQuestion = {
          id: `q-${Date.now()}`,
          question: newQuestion,
          answer: mockAnswer,
          timestamp: new Date().toISOString()
        };
        
        setQuestions([newQuestionObj, ...questions]);
        setNewQuestion('');
        setAskingQuestion(false);
      }, 2000);
    } catch (err) {
      setError('Failed to send your question. Please try again.');
      setAskingQuestion(false);
    }
  };

  const scheduleConsultation = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newConsultation.date || !newConsultation.time) return;
    
    try {
      // In a real app, this would be an API call to schedule the consultation
      // For now, simulate a delay and add a mock consultation
      setTimeout(() => {
        const dateTimeString = `${newConsultation.date}T${newConsultation.time}`;
        
        const newConsultationObj: StylistConsultation = {
          id: `cons-${Date.now()}`,
          title: 'Personal Styling Session',
          dateTime: new Date(dateTimeString).toISOString(),
          status: 'scheduled',
          duration: newConsultation.duration,
          stylistName: 'Emma Rodriguez',
          notes: newConsultation.notes
        };
        
        setConsultations([...consultations, newConsultationObj]);
        setNewConsultation({
          date: '',
          time: '',
          duration: 30,
          notes: ''
        });
        setNewConsultationModal(false);
      }, 1000);
    } catch (err) {
      setError('Failed to schedule consultation. Please try again.');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };
  
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };
  
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return `${formatDate(dateString)} at ${date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    })}`;
  };
  
  const isUpcoming = (dateString: string) => {
    const date = new Date(dateString);
    return date > new Date();
  };

  const sortedConsultations = [...consultations].sort((a, b) => {
    // Sort by status (scheduled first, then completed, then cancelled)
    if (a.status !== b.status) {
      if (a.status === 'scheduled') return -1;
      if (b.status === 'scheduled') return 1;
      if (a.status === 'completed') return -1;
      if (b.status === 'completed') return 1;
    }
    
    // Then by date (upcoming first, then past)
    const dateA = new Date(a.dateTime);
    const dateB = new Date(b.dateTime);
    return dateB.getTime() - dateA.getTime();
  });
  
  const renderConsultations = () => (
    <div className="consultations-section">
      <div className="section-header">
        <h2>Your Stylist Consultations</h2>
        <button 
          className="schedule-button"
          onClick={() => setNewConsultationModal(true)}
        >
          Schedule New
        </button>
      </div>
      
      {sortedConsultations.length === 0 ? (
        <div className="empty-state">
          <CalendarClock size={48} />
          <h3>No consultations scheduled</h3>
          <p>Book a personalized styling session with one of our expert stylists.</p>
          <button 
            className="schedule-button"
            onClick={() => setNewConsultationModal(true)}
          >
            Schedule Consultation
          </button>
        </div>
      ) : (
        <div className="consultations-list">
          {sortedConsultations.map(consultation => (
            <div 
              key={consultation.id} 
              className={`consultation-card ${consultation.status}`}
            >
              {consultation.status === 'scheduled' && isUpcoming(consultation.dateTime) && (
                <div className="consultation-badge upcoming">Upcoming</div>
              )}
              {consultation.status === 'completed' && (
                <div className="consultation-badge completed">Completed</div>
              )}
              {consultation.status === 'cancelled' && (
                <div className="consultation-badge cancelled">Cancelled</div>
              )}
              
              <div className="consultation-header">
                <h3>{consultation.title}</h3>
                <div className="consultation-stylist">
                  <User size={16} />
                  <span>{consultation.stylistName}</span>
                </div>
              </div>
              
              <div className="consultation-details">
                <div className="consultation-date">
                  <Calendar size={16} />
                  <span>{formatDate(consultation.dateTime)}</span>
                </div>
                <div className="consultation-time">
                  <Clock size={16} />
                  <span>{formatTime(consultation.dateTime)}</span>
                </div>
                <div className="consultation-duration">
                  <span>{consultation.duration} minutes</span>
                </div>
              </div>
              
              {consultation.notes && (
                <div className="consultation-notes">
                  <p>{consultation.notes}</p>
                </div>
              )}
              
              <div className="consultation-actions">
                {consultation.status === 'scheduled' && isUpcoming(consultation.dateTime) && (
                  <>
                    <button className="secondary-button">Reschedule</button>
                    <button className="primary-button">Join Meeting</button>
                  </>
                )}
                {consultation.status === 'completed' && (
                  <button className="primary-button">View Summary</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
  
  const renderQuickQuestions = () => (
    <div className="questions-section">
      <div className="section-header">
        <h2>Ask a Quick Style Question</h2>
      </div>
      
      <div className="ask-question-form">
        <form onSubmit={handleAskQuestion}>
          <div className="question-input-container">
            <textarea
              placeholder="Ask our AI stylist anything about fashion, outfits, or styling advice..."
              value={newQuestion}
              onChange={(e) => setNewQuestion(e.target.value)}
              disabled={askingQuestion}
              rows={3}
              className="question-input"
            />
            <button 
              type="submit"
              className="send-question"
              disabled={askingQuestion || !newQuestion.trim()}
            >
              {askingQuestion ? <Loader size={20} className="spinner" /> : <Send size={20} />}
            </button>
          </div>
        </form>
      </div>
      
      <div className="question-suggestions">
        <h3>Popular Questions</h3>
        <div className="suggestion-buttons">
          <button 
            onClick={() => setNewQuestion("What should I wear to a job interview in the tech industry?")}
            className="suggestion-button"
          >
            What should I wear to a job interview in the tech industry?
          </button>
          <button 
            onClick={() => setNewQuestion("How can I style one dress for different occasions?")}
            className="suggestion-button"
          >
            How can I style one dress for different occasions?
          </button>
          <button 
            onClick={() => setNewQuestion("What are the essential pieces for a capsule wardrobe?")}
            className="suggestion-button"
          >
            What are the essential pieces for a capsule wardrobe?
          </button>
        </div>
      </div>
      
      <div className="previous-questions">
        <h3>Your Questions History</h3>
        
        {questions.length === 0 ? (
          <div className="empty-questions">
            <HelpCircle size={32} />
            <p>You haven't asked any questions yet</p>
          </div>
        ) : (
          <div className="questions-list">
            {questions.map(question => (
              <div key={question.id} className="question-answer-card">
                <div className="question-container">
                  <div className="question-meta">
                    <MessageSquare size={16} className="question-icon" />
                    <span className="question-timestamp">{formatDate(question.timestamp)}</span>
                  </div>
                  <div className="question-text">
                    <p>{question.question}</p>
                  </div>
                </div>
                
                <div className="answer-container">
                  <div className="answer-text">
                    <p>{question.answer}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
  
  const renderRecommendations = () => (
    <div className="recommendations-section">
      <div className="section-header">
        <h2>Your Style Recommendations</h2>
        <button 
          className="refresh-button"
          onClick={() => fetchStylistData()}
        >
          Refresh
        </button>
      </div>
      
      {recommendations.length === 0 ? (
        <div className="empty-state">
          <Image size={48} />
          <h3>No recommendations yet</h3>
          <p>Complete your style profile or schedule a consultation to get personalized recommendations.</p>
          <button 
            className="primary-button"
            onClick={() => navigate('/style-analysis')}
          >
            Complete Style Profile
          </button>
        </div>
      ) : (
        <div className="recommendations-list">
          {recommendations.map(recommendation => (
            <div key={recommendation.id} className="recommendation-card">
              <div className="recommendation-header">
                <h3>{recommendation.title}</h3>
                <span className="recommendation-date">{formatDate(recommendation.timestamp)}</span>
              </div>
              
              <p className="recommendation-description">{recommendation.description}</p>
              
              <div className="recommended-items">
                {recommendation.items.map(item => (
                  <div key={item.id} className="recommended-item">
                    <div className="item-image">
                      <img src={item.image} alt={item.name} />
                    </div>
                    <div className="item-details">
                      <h4>{item.name}</h4>
                      <div className="item-price">${item.price.toFixed(2)}</div>
                      <a href={item.url} className="view-item">
                        View Product <ChevronRight size={14} />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="recommendation-actions">
                <button className="secondary-button">Save to Favorites</button>
                <button className="primary-button">Shop All Items</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="ai-stylist-container">
      <Header />
      
      <main className="ai-stylist-main">
        <div className="ai-stylist-header">
          <h1>Your AI Stylist</h1>
          <p>Get personalized style advice, outfit recommendations, and fashion consultations</p>
        </div>
        
        <div className="ai-stylist-tabs">
          <button 
            className={`tab-button ${activeTab === 'consultations' ? 'active' : ''}`}
            onClick={() => setActiveTab('consultations')}
          >
            <CalendarClock size={20} />
            <span>Consultations</span>
          </button>
          <button 
            className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`}
            onClick={() => setActiveTab('questions')}
          >
            <MessageSquare size={20} />
            <span>Quick Questions</span>
          </button>
          <button 
            className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommendations')}
          >
            <AlignLeft size={20} />
            <span>Recommendations</span>
          </button>
        </div>
        
        {loading ? (
          <div className="loading-state">
            <Loader size={40} className="spinner" />
            <p>Loading your stylist data...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <p>{error}</p>
            <button 
              onClick={fetchStylistData}
              className="retry-button"
            >
              Try Again
            </button>
          </div>
        ) : (
          <div className="ai-stylist-content">
            {activeTab === 'consultations' && renderConsultations()}
            {activeTab === 'questions' && renderQuickQuestions()}
            {activeTab === 'recommendations' && renderRecommendations()}
          </div>
        )}
      </main>
      
      {newConsultationModal && (
        <div className="modal-overlay">
          <div className="consultation-modal">
            <div className="modal-header">
              <h2>Schedule a Consultation</h2>
              <button 
                className="close-modal"
                onClick={() => setNewConsultationModal(false)}
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={scheduleConsultation}>
              <div className="form-group">
                <label htmlFor="consultation-date">Date</label>
                <input
                  type="date"
                  id="consultation-date"
                  value={newConsultation.date}
                  onChange={(e) => setNewConsultation({...newConsultation, date: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="consultation-time">Time</label>
                <input
                  type="time"
                  id="consultation-time"
                  value={newConsultation.time}
                  onChange={(e) => setNewConsultation({...newConsultation, time: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="consultation-duration">Duration</label>
                <select
                  id="consultation-duration"
                  value={newConsultation.duration}
                  onChange={(e) => setNewConsultation({...newConsultation, duration: Number(e.target.value)})}
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={45}>45 minutes</option>
                  <option value={60}>60 minutes</option>
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="consultation-notes">Notes (optional)</label>
                <textarea
                  id="consultation-notes"
                  value={newConsultation.notes}
                  onChange={(e) => setNewConsultation({...newConsultation, notes: e.target.value})}
                  rows={3}
                  placeholder="Describe what you'd like to discuss during your consultation..."
                />
              </div>
              
              <div className="form-actions">
                <button 
                  type="button"
                  className="cancel-button"
                  onClick={() => setNewConsultationModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="submit-button"
                >
                  Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIStylist; 