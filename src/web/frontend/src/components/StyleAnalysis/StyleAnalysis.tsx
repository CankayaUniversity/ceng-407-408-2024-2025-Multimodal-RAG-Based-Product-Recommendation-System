import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../Header/Header';
import { 
  Palette, 
  TrendingUp, 
  Upload, 
  Camera, 
  CheckCircle, 
  Loader,
  X
} from 'lucide-react';
import './StyleAnalysis.css';

interface StyleProfile {
  colors: string[];
  styles: string[];
  bodyType: string;
  season: string;
  recommendations: StyleRecommendation[];
}

interface StyleRecommendation {
  category: string;
  items: StyleItem[];
}

interface StyleItem {
  name: string;
  description: string;
  reason: string;
}

const StyleAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [styleProfile, setStyleProfile] = useState<StyleProfile | null>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  
  // Questions for style quiz
  const [answers, setAnswers] = useState({
    casualStyle: '',
    formalStyle: '',
    colorPreference: '',
    patternPreference: '',
    accessoryPreference: '',
    seasonPreference: '',
    bodyType: '',
    ageRange: '',
    fashionGoals: [] as string[]
  });

  // Body type options for identification
  const bodyTypes = [
    { id: 'rectangle', name: 'Rectangle', description: 'Shoulders and hips aligned, minimal waist definition' },
    { id: 'hourglass', name: 'Hourglass', description: 'Shoulders and hips aligned, defined waist' },
    { id: 'pear', name: 'Pear/Triangle', description: 'Hips wider than shoulders, defined waist' },
    { id: 'inverted-triangle', name: 'Inverted Triangle', description: 'Shoulders wider than hips, less defined waist' },
    { id: 'apple', name: 'Apple/Oval', description: 'Fuller midsection, slimmer legs and arms' }
  ];
  
  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login', { state: { from: '/style-analysis' } });
      return;
    }
    
    // Fetch existing style profile if available
    fetchStyleProfile();
  }, [navigate]);
  
  const fetchStyleProfile = async () => {
    try {
      setLoading(true);
      
      setTimeout(() => {
        // Check if user has an existing profile
        const savedProfile = localStorage.getItem('styleProfile');
        if (savedProfile) {
          setStyleProfile(JSON.parse(savedProfile));
          setActiveStep(4); // Skip to results
        }
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError('Failed to load your style profile. Please try again.');
      setLoading(false);
    }
  };
  
  const handleNextStep = () => {
    setActiveStep(prev => prev + 1);
  };
  
  const handlePrevStep = () => {
    setActiveStep(prev => prev - 1);
  };
  
  const handleAnswerChange = (question: string, value: string | string[]) => {
    setAnswers(prev => ({
      ...prev,
      [question]: value
    }));
  };
  
  const toggleFashionGoal = (goal: string) => {
    setAnswers(prev => {
      const currentGoals = [...(prev.fashionGoals as string[]) || []];
      if (currentGoals.includes(goal)) {
        return {
          ...prev,
          fashionGoals: currentGoals.filter(g => g !== goal)
        };
      } else {
        return {
          ...prev,
          fashionGoals: [...currentGoals, goal]
        };
      }
    });
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleCameraToggle = async () => {
    if (cameraActive) {
      // Stop camera
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
      setCameraActive(false);
    } else {
      // Start camera
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setCameraActive(true);
      } catch (err) {
        setError('Unable to access camera. Please check permissions.');
      }
    }
  };
  
  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw the current video frame on the canvas
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to data URL
        const dataUrl = canvas.toDataURL('image/jpeg');
        setImagePreview(dataUrl);
        
        // Convert data URL to file
        fetch(dataUrl)
          .then(res => res.blob())
          .then(blob => {
            const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
            setImageFile(file);
          });
        
        // Stop camera
        handleCameraToggle();
      }
    }
  };
  
  const clearPhoto = () => {
    setImageFile(null);
    setImagePreview(null);
  };
  
  const analyzeStyle = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be an API call that processes the image
      // For now, we'll simulate a response with mock data
      
      setTimeout(() => {
        // Mock style profile
        const mockProfile: StyleProfile = {
          colors: ['Navy', 'Burgundy', 'Forest Green', 'Charcoal'],
          styles: ['Classic', 'Business Casual', 'Smart Casual'],
          bodyType: answers.bodyType || 'rectangle',
          season: 'Autumn',
          recommendations: [
            {
              category: 'Tops',
              items: [
                {
                  name: 'V-neck sweaters',
                  description: 'Medium weight in solid colors or subtle patterns',
                  reason: 'Flatters your body type and complements your color palette'
                },
                {
                  name: 'Button-down shirts',
                  description: 'Slightly fitted in solid colors or subtle stripes',
                  reason: 'Provides structure and aligns with your classic style preference'
                }
              ]
            },
            {
              category: 'Bottoms',
              items: [
                {
                  name: 'Straight-leg pants',
                  description: 'Mid-rise in navy, charcoal or earth tones',
                  reason: 'Creates balanced proportions for your body type'
                },
                {
                  name: 'Dark wash jeans',
                  description: 'Medium rise with minimal distressing',
                  reason: 'Versatile option that works with your preferred style'
                }
              ]
            },
            {
              category: 'Outerwear',
              items: [
                {
                  name: 'Structured blazer',
                  description: 'Single-breasted with minimal details',
                  reason: 'Adds definition to your silhouette and elevates casual looks'
                },
                {
                  name: 'Field jacket',
                  description: 'Medium weight in olive or navy',
                  reason: 'Practical option that complements your color palette'
                }
              ]
            }
          ]
        };
        
        // Save to state and local storage
        setStyleProfile(mockProfile);
        localStorage.setItem('styleProfile', JSON.stringify(mockProfile));
        
        // Move to results
        setActiveStep(4);
        setLoading(false);
      }, 2000);
    } catch (err) {
      setError('Failed to analyze your style. Please try again.');
      setLoading(false);
    }
  };
  
  // Render different steps of the style analysis
  const renderStep = () => {
    switch (activeStep) {
      case 1:
        return (
          <div className="style-step">
            <h2>Style Preferences Quiz</h2>
            <p className="step-description">
              Let's start by understanding your fashion preferences
            </p>
            
            <div className="question-group">
              <label>What's your preferred casual style?</label>
              <div className="options-group">
                {['Relaxed', 'Sporty', 'Preppy', 'Bohemian', 'Minimalist'].map(style => (
                  <div 
                    key={style}
                    className={`style-option ${answers.casualStyle === style ? 'selected' : ''}`}
                    onClick={() => handleAnswerChange('casualStyle', style)}
                  >
                    {style}
                    {answers.casualStyle === style && <CheckCircle size={18} />}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="question-group">
              <label>What's your preferred formal style?</label>
              <div className="options-group">
                {['Classic', 'Modern', 'Glamorous', 'Eclectic', 'Minimalist'].map(style => (
                  <div 
                    key={style}
                    className={`style-option ${answers.formalStyle === style ? 'selected' : ''}`}
                    onClick={() => handleAnswerChange('formalStyle', style)}
                  >
                    {style}
                    {answers.formalStyle === style && <CheckCircle size={18} />}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="question-group">
              <label>Which color palette do you prefer?</label>
              <div className="options-group">
                {[
                  'Neutrals (black, white, gray, beige)',
                  'Earth tones (olive, burgundy, rust, brown)',
                  'Bright colors (red, yellow, blue)',
                  'Pastels (light pink, baby blue, mint)',
                  'Jewel tones (emerald, sapphire, ruby)'
                ].map(color => (
                  <div 
                    key={color}
                    className={`style-option ${answers.colorPreference === color ? 'selected' : ''}`}
                    onClick={() => handleAnswerChange('colorPreference', color)}
                  >
                    {color}
                    {answers.colorPreference === color && <CheckCircle size={18} />}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="question-group">
              <label>What are your fashion goals? (Select all that apply)</label>
              <div className="options-group">
                {[
                  'Look more professional',
                  'Express my personality',
                  'Feel more confident',
                  'Build a capsule wardrobe',
                  'Stay on trend',
                  'Find my signature look'
                ].map(goal => (
                  <div 
                    key={goal}
                    className={`style-option ${(answers.fashionGoals as string[])?.includes(goal) ? 'selected' : ''}`}
                    onClick={() => toggleFashionGoal(goal)}
                  >
                    {goal}
                    {(answers.fashionGoals as string[])?.includes(goal) && <CheckCircle size={18} />}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="step-buttons">
              <button 
                className="step-button next"
                onClick={handleNextStep}
                disabled={!answers.casualStyle || !answers.colorPreference || !(answers.fashionGoals as string[])?.length}
              >
                Next Step
              </button>
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="style-step">
            <h2>Body Type Identification</h2>
            <p className="step-description">
              Understanding your body shape helps us recommend flattering styles
            </p>
            
            <div className="body-types-grid">
              {bodyTypes.map(type => (
                <div 
                  key={type.id}
                  className={`body-type-card ${answers.bodyType === type.id ? 'selected' : ''}`}
                  onClick={() => handleAnswerChange('bodyType', type.id)}
                >
                  <div className="body-type-image">
                    <img 
                      src={`/images/body-types/${type.id}.svg`} 
                      alt={type.name}
                      onError={(e) => {
                        e.currentTarget.src = `https://via.placeholder.com/150?text=${type.name}`;
                      }}
                    />
                  </div>
                  <div className="body-type-info">
                    <h3>{type.name}</h3>
                    <p>{type.description}</p>
                  </div>
                  {answers.bodyType === type.id && (
                    <div className="body-type-selected">
                      <CheckCircle size={24} />
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <div className="step-buttons">
              <button 
                className="step-button prev"
                onClick={handlePrevStep}
              >
                Previous
              </button>
              <button 
                className="step-button next"
                onClick={handleNextStep}
                disabled={!answers.bodyType}
              >
                Next Step
              </button>
            </div>
          </div>
        );
        
      case 3:
        return (
          <div className="style-step">
            <h2>Photo Analysis</h2>
            <p className="step-description">
              Upload a full-body photo or a photo of your wardrobe for AI analysis (optional)
            </p>
            
            <div className="photo-upload-section">
              {!imagePreview ? (
                <div className="upload-methods">
                  <div className="upload-method">
                    <label htmlFor="photo-upload" className="upload-button">
                      <Upload size={24} />
                      Choose Photo
                    </label>
                    <input 
                      id="photo-upload" 
                      type="file" 
                      accept="image/*" 
                      onChange={handleFileChange}
                      style={{ display: 'none' }}
                    />
                  </div>
                  
                  <div className="upload-method">
                    <button 
                      className="camera-button"
                      onClick={handleCameraToggle}
                    >
                      <Camera size={24} />
                      Take Photo
                    </button>
                  </div>
                </div>
              ) : (
                <div className="photo-preview">
                  <img src={imagePreview} alt="Preview" />
                  <button 
                    className="clear-photo"
                    onClick={clearPhoto}
                  >
                    <X size={20} />
                  </button>
                </div>
              )}
              
              {cameraActive && (
                <div className="camera-view">
                  <video 
                    ref={videoRef}
                    autoPlay
                    playsInline
                  />
                  <div className="camera-controls">
                    <button 
                      className="capture-button"
                      onClick={capturePhoto}
                    >
                      Capture
                    </button>
                    <button 
                      className="cancel-button"
                      onClick={handleCameraToggle}
                    >
                      Cancel
                    </button>
                  </div>
                  <canvas ref={canvasRef} style={{ display: 'none' }} />
                </div>
              )}
            </div>
            
            <div className="photo-tips">
              <h3>Tips for best results:</h3>
              <ul>
                <li>Use good lighting (natural light works best)</li>
                <li>For body type analysis, wear fitted clothing</li>
                <li>For wardrobe analysis, lay out items clearly</li>
                <li>Make sure the image is clear and in focus</li>
              </ul>
            </div>
            
            <div className="skip-notice">
              <p>You can skip this step if you prefer not to upload a photo.</p>
            </div>
            
            <div className="step-buttons">
              <button 
                className="step-button prev"
                onClick={handlePrevStep}
              >
                Previous
              </button>
              <button 
                className="step-button analyze"
                onClick={analyzeStyle}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader size={20} className="spinner" />
                    Analyzing...
                  </>
                ) : 'Analyze Style'}
              </button>
              <button 
                className="step-button skip"
                onClick={() => analyzeStyle()}
                disabled={loading}
              >
                Skip & Continue
              </button>
            </div>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        );
        
      case 4:
        return (
          <div className="style-step results">
            <h2>Your Style Analysis Results</h2>
            
            {loading ? (
              <div className="loading-results">
                <Loader size={40} className="spinner" />
                <p>Analyzing your style preferences...</p>
              </div>
            ) : styleProfile ? (
              <div className="style-results">
                <div className="results-section">
                  <h3>Your Color Palette</h3>
                  <div className="color-palette">
                    {styleProfile.colors.map(color => (
                      <div key={color} className="color-item">
                        <div 
                          className="color-swatch"
                          style={{ backgroundColor: color.toLowerCase() }}
                        />
                        <span>{color}</span>
                      </div>
                    ))}
                  </div>
                  <p className="result-explanation">
                    These colors complement your natural features and work well with your style preferences.
                  </p>
                </div>
                
                <div className="results-section">
                  <h3>Your Style Definition</h3>
                  <div className="style-tags">
                    {styleProfile.styles.map(style => (
                      <div key={style} className="style-tag">
                        {style}
                      </div>
                    ))}
                  </div>
                  <p className="result-explanation">
                    Your style combines elements from these aesthetic categories based on your preferences.
                  </p>
                </div>
                
                <div className="results-section">
                  <h3>Body Type: {bodyTypes.find(t => t.id === styleProfile.bodyType)?.name}</h3>
                  <p className="result-explanation">
                    Understanding your body type helps identify silhouettes and cuts that flatter your natural shape.
                  </p>
                </div>
                
                <div className="results-section recommendations">
                  <h3>Personalized Recommendations</h3>
                  
                  {styleProfile.recommendations.map(category => (
                    <div key={category.category} className="recommendation-category">
                      <h4>{category.category}</h4>
                      <div className="recommendation-items">
                        {category.items.map((item, index) => (
                          <div key={index} className="recommendation-item">
                            <h5>{item.name}</h5>
                            <p className="item-description">{item.description}</p>
                            <div className="item-reason">
                              <strong>Why:</strong> {item.reason}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="results-actions">
                  <button 
                    className="result-action primary"
                    onClick={() => navigate('/browse')}
                  >
                    Shop Recommendations
                  </button>
                  <button 
                    className="result-action secondary"
                    onClick={() => navigate('/stylist')}
                  >
                    Get Styling Advice
                  </button>
                  <button 
                    className="result-action tertiary"
                    onClick={() => {
                      localStorage.removeItem('styleProfile');
                      setStyleProfile(null);
                      setActiveStep(1);
                      setAnswers({
                        casualStyle: '',
                        formalStyle: '',
                        colorPreference: '',
                        patternPreference: '',
                        accessoryPreference: '',
                        seasonPreference: '',
                        bodyType: '',
                        ageRange: '',
                        fashionGoals: []
                      });
                    }}
                  >
                    Retake Quiz
                  </button>
                </div>
              </div>
            ) : (
              <div className="error-state">
                <p>Unable to load your style profile. Please try again.</p>
                <button 
                  onClick={() => setActiveStep(1)}
                  className="retry-button"
                >
                  Start Over
                </button>
              </div>
            )}
          </div>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="style-analysis-container">
      <Header />
      <main className="style-analysis-main">
        <div className="style-analysis-header">
          <div className="header-icon">
            <Palette size={32} />
          </div>
          <h1>Personal Style Analysis</h1>
          <p>Discover your unique style profile and get personalized recommendations</p>
        </div>
        
        {loading && activeStep < 4 ? (
          <div className="loading-state">
            <Loader size={40} className="spinner" />
            <p>Analyzing your style preferences...</p>
          </div>
        ) : (
          <>
            <div className="progress-tracker">
              {Array.from({ length: 4 }).map((_, index) => (
                <div 
                  key={index}
                  className={`progress-step ${activeStep > index + 1 ? 'completed' : activeStep === index + 1 ? 'active' : ''}`}
                >
                  <div className="step-number">{index + 1}</div>
                  <div className="step-label">
                    {index === 0 ? 'Preferences' : 
                     index === 1 ? 'Body Type' : 
                     index === 2 ? 'Analysis' : 'Results'}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="style-analysis-content">
              {renderStep()}
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default StyleAnalysis; 