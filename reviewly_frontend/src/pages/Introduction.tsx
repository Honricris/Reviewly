// IntroPage.tsx
import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Introduction.css";

const features = [
  {
    title: "Conversational Chatbot",
    description: "Ask about product quality, issues, or alternative recommendations with ease.",
  },
  {
    title: "Sentiment Analysis",
    description: "Get insights on customer opinions: positive, negative, or neutral.",
  },
  {
    title: "Review Summarization",
    description: "Quickly understand key points and complaints about a product.",
  },
];

const IntroPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="intro-container">
      <section className="banner">
        <div className="banner-content">
          <h1 className="banner-title">Welcome to Reviewly</h1>
          <p className="banner-description">
            Discover insights, analyze reviews, and make informed decisions with our advanced chatbot and sentiment analysis tools.
          </p>
          <button className="try-button" onClick={() => navigate("/products")}>Try for Free</button>
        </div>
      </section>

      <section className="features">
        <h2 className="features-title">Key Features</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div className="feature-card" key={index}>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default IntroPage;
