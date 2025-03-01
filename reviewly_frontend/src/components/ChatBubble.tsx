import React, { useState, useEffect } from 'react';
import { ThreeDots } from 'react-loader-spinner'; 
import '../styles/ChatBubble.css';
import chatService from '../services/chatService';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'; 
import ChatIcon from '@mui/icons-material/Chat';
import ReactMarkdown from 'react-markdown';

const BotMessage = ({ text }) => {
  return (
    <div className="bot-message">
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  );
};


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
      text: "Hello! I am your virtual shopping assistant. I can help you find the perfect product and provide detailed information about our items. How can I assist you today?",
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
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}${queryEndpoint}`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: currentMessage }),
      });
  
      if (!response.ok) {
        throw new Error(`Error en la respuesta: ${response.status} ${response.statusText}`);
      }
      
      if (!response.body) throw new Error("No response body");
  
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let botMessage = { sender: 'bot' as const, text: '', time: new Date().toLocaleTimeString() };
  
      setMessages((prev) => [...prev, botMessage]); 
  
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
  
        if(chunk){
          botMessage.text += chunk;
          setMessages((prev) => [...prev.slice(0, -1), { ...botMessage }]);
        }
      }
  
      if (onResponse) {
        onResponse(botMessage);
      }
    } catch (error) {
      console.error("Error in sendMessage:", error);
      
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`, time: new Date().toLocaleTimeString() }
      ]);
    }finally {
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
                {message.sender === 'bot' ? <BotMessage text={message.text} /> : <div className="message-text">{message.text}</div>}
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
