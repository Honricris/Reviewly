import React, { useState } from 'react';
import MinimizeIcon from '@mui/icons-material/Minimize';
import chatbotIcon from '../assets/chatbot.png';
import '../styles/ChatMenuPage.css';

interface ChatMenuPageProps {
  onCloseClick: () => void;
  onChatClick: () => void; 
}

const ChatMenuPage: React.FC<ChatMenuPageProps> = ({ onCloseClick, onChatClick}) => {
  const [selectedModel, setSelectedModel] = useState('');
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

  const availableModels = [
    'General Assistant',
    'Product Expert',
    'Technical Support',
    'Order Specialist'
  ];

  const handleModelSelect = (model: string) => {
    setSelectedModel(model);
    setIsModelDropdownOpen(false);
  };

  return (
    <div className="chat-menu-container">
      <div className="chat-menu-header">
        <div className="header-content">
          <img src={chatbotIcon} alt="Chatbot" className="menu-chatbot-icon" />
          <h2>Virtual Shopping Assistant</h2>
          <p>How can I help you today?</p>
        </div>
        <button className="close-button" onClick={onCloseClick}>
          <MinimizeIcon style={{ color: '#2196f3', fontSize: '28px' }} />
        </button>
      </div>

      <div className="doubt-container">
        <div className="doubt-text">Have any doubts?</div>
        <button 
          className="chat-button"
          onClick={onChatClick} 
        >
          Chat with us
        </button>
      </div>

      <div className="model-selector-container">
        <div className="model-selector-label">Select the model you want to chat with:</div>
        <div 
          className={`model-dropdown ${isModelDropdownOpen ? 'open' : ''}`}
          onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
        >
          <div className="model-dropdown-header">
            {selectedModel || 'Choose a model'}
            <span className={`dropdown-arrow ${isModelDropdownOpen ? 'up' : 'down'}`}></span>
          </div>
          {isModelDropdownOpen && (
            <div className="model-dropdown-options">
              {availableModels.map(model => (
                <div 
                  key={model} 
                  className="model-option"
                  onClick={() => handleModelSelect(model)}
                >
                  {model}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMenuPage;