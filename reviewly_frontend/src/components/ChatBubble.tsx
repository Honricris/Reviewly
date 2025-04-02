import React, { useState, useEffect, useRef } from 'react';
import { ThreeDots } from 'react-loader-spinner'; 
import '../styles/ChatBubble.css';
import chatService from '../services/chatService';
import ReactMarkdown from 'react-markdown';
import chatbotIcon from '../assets/chatbot.png'; 
import MinimizeIcon from '@mui/icons-material/Minimize';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ChatMenuPage from '../components/ChatMenuPage';



interface BotMessageProps {
  text: string;
  className?: string; 
}

const BotMessage = ({ text, className }: BotMessageProps) => {
  return (
    <div className={`bot-message-content ${className || ''}`}>
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  );
};

interface ChatBubbleProps {
  onClick: () => void;
  isOpen: boolean;
  productId?: string;
  onResponse?: (botAnswer: any) => void; 
  scrollToHighlightedReview?: (reviewId: number) => void;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ onClick, isOpen, productId, onResponse, scrollToHighlightedReview }) => {
  const [messages, setMessages] = useState<{ sender: 'user' | 'bot'; text: string; time: string; reviewIds?: number[]; isStatus?: boolean}[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showMenuPage, setShowMenuPage] = useState(true);


  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const initialMessage = {
      sender: 'bot' as const,
      text: "Hello! I am your virtual shopping assistant. I can help you find the perfect product and provide detailed information about our items. How can I assist you today?",
      time: new Date().toLocaleTimeString(),
    };
    setMessages([initialMessage]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

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
      const reader = await chatService.queryChat(currentMessage, productId);
      const decoder = new TextDecoder();
  
      let botMessage = { 
        sender: 'bot' as const, 
        text: '', 
        time: new Date().toLocaleTimeString(),
        reviewIds: [] as number[],
        products: [] as any[],
        isStatus: false
      };
  
      setMessages((prev) => [...prev, botMessage]);
  
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
  
        const chunk = decoder.decode(value, { stream: true });
  
        if (chunk) {
          try {
            const parsedChunk = JSON.parse(chunk);
            if (parsedChunk.type === 'additional_data') {
              botMessage.reviewIds = parsedChunk.data.review_ids || [];
              botMessage.products = parsedChunk.data.products || [];

              if (botMessage.products.length > 0 && onResponse) {
                onResponse({ products: botMessage.products });
              } else if (botMessage.reviewIds.length > 0 && onResponse) {
                onResponse({ reviews: botMessage.reviewIds });
              }

            }else if (parsedChunk.type === 'status') {

              const statusMessage = {
                sender: 'bot' as const,
                text: parsedChunk.message,
                time: new Date().toLocaleTimeString(),
                isStatus: true
              };
              setMessages((prev) => [...prev.slice(0, -1), statusMessage]);
              setIsLoading(false); 

            } else {
              setMessages((prev) => prev.filter(msg => !msg.isStatus));
              botMessage.text += chunk;
              setMessages((prev) => [...prev.slice(0, -1), { ...botMessage }]);

            }
          } catch (error) {
            botMessage.text += chunk;
            setMessages((prev) => [...prev.slice(0, -1), { ...botMessage }]);
          }
        }
      }
  
    } catch (error) {
      console.error("Error in sendMessage:", error);
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`, time: new Date().toLocaleTimeString(), reviewIds: [] }
      ]);
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
          {showMenuPage ? (
            <ChatMenuPage 
              onCloseClick={onClick }
              onChatClick={() => setShowMenuPage(false)}
            
            />
          ) : (
            <>
              <div className="chat-header">
                <div className="header-left">
                  <ArrowBackIcon 
                    style={{ color: 'black', fontSize: '24px', marginRight: '10px' }} 
                    onClick={() => setShowMenuPage(true)}
                  />      
                </div>
                <div className="header-center">
                  <img src={chatbotIcon} alt="Chatbot" className="chatbot-icon" />
                  <div className="chatbot-title">ChatBot</div>
                </div>
                <div className="close-button" onClick={onClick}>
                  <MinimizeIcon style={{ color: 'black', fontSize: '35px' }} />
                </div>
              </div>
              <div className="chat-messages">
                {messages.map((message, index) => (
                  <div key={index} className={`message-container ${message.sender}`}>
                    {message.sender === 'bot' && (
                      <img src={chatbotIcon} alt="Chatbot" className="message-icon" />
                    )}
                    <div className={`chat-message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                      {message.sender === 'bot' ? (
                        <BotMessage text={message.text} className={message.isStatus ? 'status-message' : ''} />
                      ) : (
                        <div className="message-text">{message.text}</div>
                      )}
                    
                      {message.sender === 'bot' && message.reviewIds && message.reviewIds.length > 0 && (
                        <div className="highlighted-reviews-buttons">
                          {message.reviewIds.map((reviewId, buttonIndex) => (
                            <button key={buttonIndex} onClick={() => scrollToHighlightedReview?.(reviewId)}>
                              Go to Review {buttonIndex + 1}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="message-container bot">
                    <img src={chatbotIcon} alt="Chatbot" className="message-icon" />
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
                  </div>
                )}
                <div ref={messagesEndRef} />
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
        </>
      )}
      {!isOpen && (
        <div className="chat-bubble" onClick={onClick}>
          <div className="checkbox-wrapper">
            <input
              name="ehs_approval"
              className="form-check-label custom-radio-label"
              id="Rejected"
              type="checkbox"
            />
            <label htmlFor="Rejected">
              <div className="tick_mark">
                <div className="cross"></div>
              </div>
            </label>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBubble;