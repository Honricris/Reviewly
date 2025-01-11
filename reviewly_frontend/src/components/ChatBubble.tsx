import React, { useState, useEffect } from 'react';
import { ThreeDots } from 'react-loader-spinner'; 
import '../styles/ChatBubble.css';
import chatService from '../services/chatService';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'; 
import ChatIcon from '@mui/icons-material/Chat';

interface ChatBubbleProps {
  onClick: () => void;
  isOpen: boolean;
  queryEndpoint: string;
  onResponse?: (botAnswer: any) => void; 
  highlightedReviewIds: number[];
  scrollToHighlightedReview: (reviewId: number) => void;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ onClick, isOpen, queryEndpoint, onResponse, highlightedReviewIds, scrollToHighlightedReview }) => {
  const [messages, setMessages] = useState<{ sender: 'user' | 'bot'; text: string; time: string; reviewIds?: number[] }[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const initialMessage = {
      sender: 'bot' as const,
      text: 'Hello! I am your virtual assistant. How can I assist you today?',
      time: new Date().toLocaleTimeString(),
    };
    setMessages([initialMessage]);
  }, []);

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage = {
      sender: 'user' as const,
      text: currentMessage,
      time: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const botAnswer = await chatService.queryChat(currentMessage, queryEndpoint);
      const botMessage = {
        sender: 'bot' as const,
        text: botAnswer.answer,
        reviewIds: botAnswer.reviews, 
        time: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botMessage]);

      if (onResponse) {
        onResponse(botAnswer); 
      }
    } catch (error) {
      const botMessage = {
        sender: 'bot' as const,
        text: 'There was an error processing your request.',
        time: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className={`chat-container ${isOpen ? 'open' : ''}`}>
      {isOpen && (
        <>
          <div className="chat-header">
            <button className="close-button" onClick={onClick}>
              <ArrowForwardIcon style={{ fontSize: 24 }} />
            </button>
          </div>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`chat-message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                <div className="message-header">
                  <span className="message-sender">{message.sender === 'user' ? '👤 User' : '🤖 Chat Bot'}</span>
                  <span className="message-time">{message.time}</span>
                </div>
                <div className="message-text">{message.text}</div>
                {/* Mostrar botones solo para el último mensaje del bot */}
                {message.sender === 'bot' && highlightedReviewIds.length > 0 && index === messages.length - 1 && (
                  <div className="highlighted-reviews-buttons">
                    {highlightedReviewIds.map((reviewId, buttonIndex) => (
                      <button 
                        key={buttonIndex} 
                        onClick={() => scrollToHighlightedReview(reviewId)}
                      >
                        Go to Review {buttonIndex + 1}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="chat-message bot-message">
                <div className="message-text">
                  <ThreeDots
                    visible={true}
                    height="30"
                    width="30"
                    color="#4fa94d"
                    radius="9"
                    ariaLabel="three-dots-loading"
                  />
                </div>
              </div>
            )}
          </div>
          <div className="chat-input-container">
            <input
              type="text"
              className="chat-input"
              placeholder="Write your message..."
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading || !currentMessage.trim()}>
              {isLoading ? '⏳' : 'Send'}
            </button>
          </div>
        </>
      )}
      {!isOpen && (
        <div className="chat-bubble" onClick={onClick}>
          <ChatIcon style={{ fontSize: 40 }} />
        </div>
      )}
    </div>
  );
};

export default ChatBubble;
