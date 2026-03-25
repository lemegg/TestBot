import React, { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';

const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  const { getToken } = useAuth();
  const [feedbackStatus, setFeedbackStatus] = useState(null); // 'submitting', 'success', 'error'
  const [submittedFeedback, setSubmittedFeedback] = useState(null); // 'like', 'dislike'

  const handleFeedback = async (type) => {
    if (!message.query_log_id) return;
    
    setFeedbackStatus('submitting');
    try {
      const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const api_base = isLocal ? `http://${window.location.hostname}:8001` : '';
      
      const token = await getToken();
      const response = await fetch(`${api_base}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query_log_id: message.query_log_id,
          feedback: type
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Feedback submission failed');
      }

      setFeedbackStatus('success');
      setSubmittedFeedback(type);
    } catch (err) {
      console.error('Feedback error:', err);
      setFeedbackStatus('error');
    }
  };
  
  if (isUser) {
    return (
      <div className="message user">
        <div className="text">{message.text}</div>
      </div>
    );
  }

  // Bot message rendering for structured answer
  const { summary, steps, rules, notes } = message.answer || {};

  // Simple function to render markdown links [Text](url)
  const renderTextWithLinks = (text) => {
    if (!text) return null;
    const parts = text.split(/(\[.*?\]\(.*?\))/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(.*?)\]\((.*?)\)/);
      if (match) {
        return (
          <a key={i} href={match[2]} target="_blank" rel="noopener noreferrer" className="inline-link">
            {match[1]}
          </a>
        );
      }
      return part;
    });
  };

  return (
    <div className="message bot">
      <div className="bot-content">
        {message.text && <p className="summary">{renderTextWithLinks(message.text)}</p>}
        {summary && <p className="summary">{renderTextWithLinks(summary)}</p>}
        
        {steps && steps.length > 0 && (
          <div className="section">
            <h4 className="section-title">Steps:</h4>
            <ol className="steps-list">
              {steps.map((step, i) => <li key={i}>{renderTextWithLinks(step)}</li>)}
            </ol>
          </div>
        )}

        {rules && rules.length > 0 && (
          <div className="section">
            <h4 className="section-title">Policies & Rules:</h4>
            <ul className="rules-list">
              {rules.map((rule, i) => <li key={i}>{renderTextWithLinks(rule)}</li>)}
            </ul>
          </div>
        )}

        {notes && notes.length > 0 && (
          <div className="section notes-section">
            {notes.map((note, i) => <p key={i} className="note-item small">{renderTextWithLinks(note)}</p>)}
          </div>
        )}

        {/* Feedback Section */}
        {message.query_log_id && (
          <div className="feedback-section">
            {feedbackStatus === 'success' ? (
              <span className="feedback-success">Feedback recorded ✓</span>
            ) : (
              <>
                <button 
                  className={`feedback-btn ${submittedFeedback === 'like' ? 'active' : ''}`}
                  onClick={() => handleFeedback('like')}
                  disabled={feedbackStatus === 'submitting'}
                  title="Helpful"
                >
                  👍
                </button>
                <button 
                  className={`feedback-btn ${submittedFeedback === 'dislike' ? 'active' : ''}`}
                  onClick={() => handleFeedback('dislike')}
                  disabled={feedbackStatus === 'submitting'}
                  title="Not Helpful"
                >
                  👎
                </button>
                {feedbackStatus === 'error' && (
                  <span className="feedback-error">Failed to send. Try again?</span>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
