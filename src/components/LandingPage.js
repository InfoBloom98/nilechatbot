import React from 'react';
import './LandingPage.css';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleStartChat = () => {
    navigate('/chat');
  };

  return (
    <div className="landing-container">
      <div className="landing-overlay">
        <div className="landing-content">
          <div className="logo-container">
            <img 
              src="/nile-university-logo.png" 
              alt="Nile University of Nigeria" 
              className="logo"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'https://www.nileuniversity.edu.ng/wp-content/uploads/2020/08/logo.png';
              }}
            />
          </div>
          
          <h1>Welcome to Nile University Assistant</h1>
          
          <p className="intro-text">
            Your AI-powered guide to all things Nile University. Get instant answers about 
            admissions, courses, tuition fees, accommodation, and more!
          </p>
          
          <div className="features">
            <div className="feature">
              <div className="feature-icon">📚</div>
              <h3>Academic Information</h3>
              <p>Learn about programs, courses, and academic requirements</p>
            </div>
            
            <div className="feature">
              <div className="feature-icon">💰</div>
              <h3>Tuition & Payments</h3>
              <p>Get details on fees, payment options, and scholarships</p>
            </div>
            
            <div className="feature">
              <div className="feature-icon">🏠</div>
              <h3>Accommodation</h3>
              <p>Find out about on-campus and off-campus housing</p>
            </div>
          </div>
          
          <button className="start-button" onClick={handleStartChat}>
            Start Chatting Now
          </button>
          
          <div className="disclaimer">
            <p>
              This AI assistant provides general information about Nile University.
              For personalized assistance, please contact the appropriate university department.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 