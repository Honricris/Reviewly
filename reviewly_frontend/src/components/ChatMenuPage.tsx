import React, { useState } from 'react';
import MinimizeIcon from '@mui/icons-material/Minimize';
import chatbotIcon from '../assets/chatbot.png';
import '../styles/ChatMenuPage.css';

interface ChatMenuPageProps {
  onCloseClick: () => void;
  onChatClick: () => void; 
}

const ChatMenuPage: React.FC<ChatMenuPageProps> = ({ onCloseClick, onChatClick}) => {
  const [selectedProvider, setSelectedProvider] = useState('OpenAI');
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

  const providerModels = {
    "OpenAI": "openai/gpt-4o-mini",
    "Anthropic": "anthropic/claude-3-haiku:beta",
    "Mistral": "Mistral/ministral-8b",
    "Amazon": "amazon/nova-micro-v1"
  };

  const availableProviders = Object.keys(providerModels);

  const handleProviderSelect = (provider: string) => {
    setSelectedProvider(provider);
    setIsModelDropdownOpen(false);
    localStorage.setItem('selectedProvider', provider);
    localStorage.setItem('selectedModel', providerModels[provider as keyof typeof providerModels]);
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
        <div className="model-selector-label">Select the provider you want to use in the chat:</div>
        <div 
          className={`model-dropdown ${isModelDropdownOpen ? 'open' : ''}`}
          onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
        >
          <div className="model-dropdown-header">
            {selectedProvider || 'Choose a provider'}
            <span className={`dropdown-arrow ${isModelDropdownOpen ? 'up' : 'down'}`}></span>
          </div>
          {isModelDropdownOpen && (
            <div className="model-dropdown-options">
              {availableProviders.map(provider => (
                <div 
                  key={provider} 
                  className="model-option"
                  onClick={() => handleProviderSelect(provider)}
                >
                  {provider}
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