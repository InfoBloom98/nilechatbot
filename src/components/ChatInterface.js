import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import SpeechRecognition from './SpeechRecognition';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm the Nile University Assistant. How can I help you today?",
      sender: 'bot',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize session ID
  useEffect(() => {
    // Generate random session ID if not exists
    const generatedSessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
    setSessionId(generatedSessionId);
    sessionStorage.setItem('sessionId', generatedSessionId);
    
    // Focus the input field when component mounts
    inputRef.current?.focus();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const playAudio = (base64Audio) => {
    if (!base64Audio) return;
    
    try {
      const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send request to backend
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          session_id: sessionId,
          voice_response: voiceEnabled,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();

      // Add bot message
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        category: data.category,
        confidence: data.confidence,
      };
      setMessages((prev) => [...prev, botMessage]);

      // Play voice if enabled and available
      if (voiceEnabled && data.voice_data) {
        playAudio(data.voice_data);
      }
    } catch (error) {
      console.error('Error:', error);
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: "Sorry, I'm having trouble connecting to the server. Please try again later.",
          sender: 'bot',
          timestamp: new Date().toISOString(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      // Focus back on input
      inputRef.current?.focus();
    }
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Set up speech recognition hooks
  const { isListening, isSupported, startListening, stopListening, recordingDuration } = SpeechRecognition({
    onSpeechResult: (data) => {
      if (data.error) {
        // Show error in a small toast or notification instead of a message
        console.error("Speech recognition error:", data.message);
      } else if (data.query) {
        // Fill the input field with the transcribed text
        setInputValue(data.query);
        
        // Focus on the input field for editing
        setTimeout(() => {
          inputRef.current?.focus();
        }, 100);
      }
      
      setIsLoading(false);
      setIsSpeaking(false);
    },
    onListening: (listening) => {
      setIsSpeaking(listening);
      if (listening) {
        setIsLoading(true);
      }
    }
  });

  // Helper function to group messages by sender
  const renderMessages = () => {
    return messages.map((message, index) => {
      const showTimestamp = index === messages.length - 1 || 
                           messages[index + 1].sender !== message.sender;
      
      return (
        <div
          key={message.id}
          className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
        >
          <div className="message-bubble">
            <p>{message.text}</p>
            {showTimestamp && (
              <span className="timestamp">{formatTime(message.timestamp)}</span>
            )}
          </div>
        </div>
      );
    });
  };

  const handleVoiceButtonClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>
          <span className="header-icon">🎓</span>
          Nile University Assistant
        </h2>
        <div className="voice-toggle" onClick={toggleVoice}>
          <label htmlFor="voice-toggle">
            {voiceEnabled ? '🔊 Voice On' : '🔈 Voice Off'}
          </label>
          <input
            id="voice-toggle"
            type="checkbox"
            checked={voiceEnabled}
            onChange={toggleVoice}
          />
        </div>
      </div>

      <div className="messages-container">
        {renderMessages()}
        {isLoading && (
          <div className="message bot">
            <div className="message-bubble typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          disabled={isLoading || isSpeaking}
          ref={inputRef}
        />
        <button 
          type="submit" 
          disabled={!inputValue.trim() || isLoading || isSpeaking}
        >
          <SendIcon />
        </button>
        <button
          type="button"
          className={`voice-button ${isListening ? 'listening' : ''}`}
          onClick={handleVoiceButtonClick}
          disabled={(isLoading && !isListening) || !isSupported}
          title={!isSupported ? "Speech recognition not supported in your browser" : isListening ? "Stop speaking" : "Start speaking"}
        >
          {isListening ? (
            <>
              <MicActiveIcon />
              <span className="recording-indication"></span>
            </>
          ) : (
            <MicIcon />
          )}
        </button>
        {isListening && (
          <div className="recording-status">
            Recording... {Math.floor(recordingDuration)} sec
          </div>
        )}
      </form>
    </div>
  );
};

const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
);

const MicIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
    <line x1="12" y1="19" x2="12" y2="23"></line>
    <line x1="8" y1="23" x2="16" y2="23"></line>
  </svg>
);

const MicActiveIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" fill="currentColor"></path>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
    <line x1="12" y1="19" x2="12" y2="23"></line>
    <line x1="8" y1="23" x2="16" y2="23"></line>
  </svg>
);

export default ChatInterface; 