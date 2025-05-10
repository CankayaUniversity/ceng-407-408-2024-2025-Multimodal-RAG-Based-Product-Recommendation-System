import React, { useState, useEffect } from "react";
import Header from "../Header/Header";
import Hero from "../Hero/Hero";
import "./LandingPage.css";
import { Bot, Search, Sparkles, Shirt, MessageSquare, TrendingUp, Calendar, User, ExternalLink, Loader } from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Link as RouterLink } from 'react-router-dom';
import Footer from '../ui/Footer';

// Define the structure of a trend article
interface TrendArticle {
  title: string;
  image_url: string;
  description: string;
  author: string;
  published_at: string;
  url: string;
  source: string;
}

function LandingPage(): React.ReactElement {
  const navigate = useNavigate();
  const [trendArticles, setTrendArticles] = useState<TrendArticle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchTrendArticles = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:3001/api/trends');
        
        if (response.data.trends) {
          // Transform the API response to match our TrendArticle structure
          const articles: TrendArticle[] = response.data.trends.map((article: any) => ({
            title: article.title || 'No Title',
            image_url: article.image_url || 'https://images.unsplash.com/photo-1581338834647-b0fb40704e21?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
            description: article.description || 'No description available',
            author: article.author || 'Unknown',
            published_at: article.published_at || new Date().toISOString(),
            url: article.url || '#',
            source: article.source || 'Fashion News',
          }));
          
          setTrendArticles(articles);
        } else {
          // Fallback data if the API doesn't return expected data
          setTrendArticles([
            {
              title: 'Summer Essentials: The Must-Have Items This Season',
              image_url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1308&q=80',
              description: 'Discover the essential items for your summer wardrobe that combine style and comfort.',
              author: 'Sarah Johnson',
              published_at: '2023-05-15T10:30:00Z',
              url: 'https://www.vogue.com',
              source: 'Vogue',
            },
            {
              title: 'Sustainable Fashion: The Rise of Eco-Friendly Brands',
              image_url: 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
              description: 'How sustainable fashion is changing the industry and which brands are leading the way.',
              author: 'Michael Chen',
              published_at: '2023-05-10T14:15:00Z',
              url: 'https://www.elle.com',
              source: 'Elle',
            },
            {
              title: 'Minimalist Style Guide: Less is More',
              image_url: 'https://images.unsplash.com/photo-1519722417352-7d6959729417?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
              description: 'The ultimate guide to achieving a minimalist wardrobe that never goes out of style.',
              author: 'Emma Wilson',
              published_at: '2023-05-05T09:45:00Z',
              url: 'https://www.harpersbazaar.com',
              source: 'Harper\'s Bazaar',
            },
            {
              title: 'Casual Elegance: Dressing Up Your Everyday Look',
              image_url: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
              description: 'Simple ways to elevate your casual outfits and make them more sophisticated.',
              author: 'David Rodriguez',
              published_at: '2023-04-28T11:20:00Z',
              url: 'https://www.cosmopolitan.com',
              source: 'Cosmopolitan',
            }
          ]);
        }
        setError(null);
      } catch (err) {
        console.error('Failed to fetch trend articles:', err);
        setError('Failed to load trend articles. Please try again later.');
        // Set fallback data
        setTrendArticles([
          {
            title: 'Summer Essentials: The Must-Have Items This Season',
            image_url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1308&q=80',
            description: 'Discover the essential items for your summer wardrobe that combine style and comfort.',
            author: 'Sarah Johnson',
            published_at: '2023-05-15T10:30:00Z',
            url: 'https://www.vogue.com',
            source: 'Vogue',
          },
          {
            title: 'Sustainable Fashion: The Rise of Eco-Friendly Brands',
            image_url: 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
            description: 'How sustainable fashion is changing the industry and which brands are leading the way.',
            author: 'Michael Chen',
            published_at: '2023-05-10T14:15:00Z',
            url: 'https://www.elle.com',
            source: 'Elle',
          },
          {
            title: 'Minimalist Style Guide: Less is More',
            image_url: 'https://images.unsplash.com/photo-1519722417352-7d6959729417?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
            description: 'The ultimate guide to achieving a minimalist wardrobe that never goes out of style.',
            author: 'Emma Wilson',
            published_at: '2023-05-05T09:45:00Z',
            url: 'https://www.harpersbazaar.com',
            source: 'Harper\'s Bazaar',
          },
          {
            title: 'Casual Elegance: Dressing Up Your Everyday Look',
            image_url: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80',
            description: 'Simple ways to elevate your casual outfits and make them more sophisticated.',
            author: 'David Rodriguez',
            published_at: '2023-04-28T11:20:00Z',
            url: 'https://www.cosmopolitan.com',
            source: 'Cosmopolitan',
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendArticles();
  }, []);
  
  // Format date to a readable format
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (e) {
      return 'Unknown date';
    }
  };
  
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Hero />

        <div className="chat-button-wrapper animate-fade-in-up">
          <button className="btn btn-primary" onClick={() => navigate("/chat")}>
            <Bot className="bot-icon" style={{ width: 28, height: 28 }} />
            Start chatting with AI for recommendations!
          </button>
        </div>

        <section className="section-container animate-fade-in-up animate-delay-1">
          <div className="section-header">
            <h2 className="section-title">Find Your Perfect Style</h2>
            <p className="section-description">
              Discover fashion recommendations tailored to your personal taste. Our AI-powered solution helps you find the perfect outfit for any occasion.
            </p>
          </div>
          
          <div className="features-section">
            <div className="feature-card animate-fade-in-up animate-delay-1">
              <div className="feature-icon">
                <Sparkles size={24} />
              </div>
              <h3 className="feature-title">AI-Powered Recommendations</h3>
              <p className="feature-description">
                Get personalized style suggestions based on your preferences and the latest fashion trends.
              </p>
            </div>
            
            <div className="feature-card animate-fade-in-up animate-delay-2">
              <div className="feature-icon">
                <Search size={24} />
              </div>
              <h3 className="feature-title">Visual Search</h3>
              <p className="feature-description">
                Upload an image of an outfit you like, and we'll find similar or complementary pieces.
              </p>
            </div>
            
            <div className="feature-card animate-fade-in-up animate-delay-3">
              <div className="feature-icon">
                <Shirt size={24} />
              </div>
              <h3 className="feature-title">Virtual Try-On</h3>
              <p className="feature-description">
                See how clothes would look on you with our virtual try-on feature before making a purchase.
              </p>
            </div>
          </div>
        </section>

        {/* Trending Articles Section */}
        <section className="section-container">
          <div className="section-header animate-fade-in-up animate-delay-2">
            <h2 className="section-title">Latest Fashion Trends</h2>
            <p className="section-description">
              Stay updated with the most recent styles and fashion trends from around the world.
            </p>
          </div>
          
          {loading ? (
            <div className="trends-loading">
              <Loader size={30} className="spinning" />
              <p>Loading latest fashion trends...</p>
            </div>
          ) : error ? (
            <div className="trends-error">
              <p>{error}</p>
            </div>
          ) : (
            <>
              <div className="trend-articles">
                {trendArticles.map((article, index) => (
                  <div key={index} className="trend-article-card animate-fade-in-up">
                    <div className="trend-article-image">
                      <img src={article.image_url} alt={article.title} />
                      <div className="trend-badge">
                        <TrendingUp size={14} />
                        <span>Trending</span>
                      </div>
                    </div>
                    <div className="trend-article-content">
                      <h3 className="trend-article-title">{article.title}</h3>
                      <p className="trend-article-excerpt">
                        {article.description.length > 120 
                          ? `${article.description.substring(0, 120)}...` 
                          : article.description}
                      </p>
                      <div className="trend-article-meta">
                        <div className="trend-article-author">
                          <User size={14} />
                          <span>{article.author}</span>
                        </div>
                        <div className="trend-article-date">
                          <Calendar size={14} />
                          <span>{formatDate(article.published_at)}</span>
                        </div>
                      </div>
                      <div className="trend-article-source">
                        Source: {article.source}
                      </div>
                      <a 
                        href={article.url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="trend-article-link"
                      >
                        <span>Read article</span>
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              <div className="view-all-trends">
                <a 
                  href="https://www.vogue.com/fashion" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="view-all-button"
                >
                  View all trends
                </a>
              </div>
            </>
          )}
        </section>

        <section className="section-container animate-fade-in-up animate-delay-3">
          <div className="section-header">
            <h2 className="section-title">Start Your Fashion Journey</h2>
            <p className="section-description">
              Get personalized recommendations by chatting with our AI assistant.
            </p>
            <div className="chat-button-wrapper" style={{ marginTop: "30px" }}>
              <button className="btn btn-primary" onClick={() => navigate("/chat")}>
                <MessageSquare size={20} />
                Chat with Fashion AI
              </button>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}

export default LandingPage;
