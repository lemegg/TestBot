import React, { useState } from 'react';
import { useUser } from '@clerk/clerk-react';

const MetadataForm = ({ onComplete }) => {
  const { user, isLoaded } = useUser();
  const [formData, setFormData] = useState({
    name: '',
    company_name: '',
    phone_number: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isLoaded) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await user.update({
        unsafeMetadata: {
          ...(user.unsafeMetadata || {}),
          name: formData.name,
          company_name: formData.company_name,
          phone_number: formData.phone_number,
          role: user.unsafeMetadata?.role || 'member'
        }
      });
      if (onComplete) onComplete();
    } catch (err) {
      console.error("Error updating metadata:", err);
      setError("Failed to update profile. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="metadata-overlay">
      <div className="metadata-modal">
        <h3>Complete Your Profile</h3>
        <p>Please provide a few more details to continue.</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address (Account)</label>
            <input 
              type="email" 
              disabled 
              value={user?.primaryEmailAddress?.emailAddress || ''} 
              style={{ backgroundColor: '#f0f0f0', color: '#666', cursor: 'not-allowed' }}
            />
          </div>

          <div className="form-group">
            <label>Full Name</label>
            <input 
              type="text" 
              required 
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="John Doe"
            />
          </div>
          
          <div className="form-group">
            <label>Company Name</label>
            <input 
              type="text" 
              required 
              value={formData.company_name}
              onChange={(e) => setFormData({...formData, company_name: e.target.value})}
              placeholder="Acme Inc."
            />
          </div>
          
          <div className="form-group">
            <label>Phone Number</label>
            <input 
              type="tel" 
              required 
              value={formData.phone_number}
              onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
              placeholder="+1 234 567 890"
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? "Saving..." : "Continue to Chat"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MetadataForm;
