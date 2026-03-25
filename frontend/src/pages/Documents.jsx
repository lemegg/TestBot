import React, { useState, useEffect, useCallback } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Upload, Trash2, FileText, Loader2 } from 'lucide-react';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState({ type: '', message: '' });
  const { getToken } = useAuth();
  const { user } = useUser();

  const role = user?.publicMetadata?.role;
  const email = user?.primaryEmailAddress?.emailAddress;
  const ADMIN_EMAIL = "worshipgate1@gmail.com";
  const isAdmin = role === 'admin' || email === ADMIN_EMAIL;

  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const API_BASE = isLocal ? `http://${window.location.hostname}:8001` : '';

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const token = await getToken();
      
      const response = await fetch(`${API_BASE}/api/docs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  }, [getToken, API_BASE]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setStatus({ type: '', message: '' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = await getToken();
      const response = await fetch(`${API_BASE}/api/docs/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (response.ok) {
        setStatus({ type: 'success', message: 'Document uploaded and processing started!' });
        await fetchData();
      } else {
        const errData = await response.json();
        setStatus({ type: 'error', message: errData.detail || 'Upload failed' });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Network error during upload' });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      const token = await getToken();
      const response = await fetch(`${API_BASE}/api/docs/${docId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setDocuments(docs => docs.filter(d => d.id !== docId));
      } else {
        alert('Failed to delete document');
      }
    } catch (error) {
      alert('Error deleting document');
    }
  };

  return (
    <>
      <header className="page-header">
        <h2>Knowledge Base</h2>
        <p className="small" style={{ color: 'var(--text-secondary)' }}>Manage the source documents for your AI chatbot</p>
      </header>

      <div className="documents-container" style={{ padding: '0 40px 40px' }}>
        {isAdmin && (
          <div className="upload-card" style={{ marginBottom: '32px' }}>
            <Upload size={32} className="upload-icon" style={{ marginBottom: 12, color: 'var(--accent-color)' }} />
            <h3>Upload Knowledge Source</h3>
            <p className="small" style={{ marginBottom: 16 }}>Supported formats: PDF, DOCX, TXT</p>
            
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
              onChange={handleUpload}
              disabled={uploading}
              className="file-input"
              id="file-upload"
              style={{ display: 'none' }}
            />
            <label htmlFor="file-upload" className={`tab-btn active ${uploading ? 'disabled' : ''}`} style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', minWidth: '200px' }}>
              {uploading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Loader2 size={16} className="animate-spin" /> Processing...
                </span>
              ) : 'Select File to Upload'}
            </label>

            {status.message && (
              <p className={`upload-status status-${status.type}`} style={{ marginTop: '12px' }}>
                {status.message}
              </p>
            )}
          </div>
        )}

        <div className="docs-table-container">
          {loading ? (
            <div className="loading-state">Loading documents...</div>
          ) : documents.length === 0 ? (
            <div className="loading-state">No knowledge sources uploaded yet.</div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '12px' }}>Document Name</th>
                  <th style={{ padding: '12px' }}>Status</th>
                  <th style={{ padding: '12px' }}>Added Date</th>
                  {isAdmin && <th style={{ padding: '12px' }}>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <FileText size={16} color="#666" />
                        {doc.name}
                      </div>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        fontSize: '12px',
                        background: doc.status === 'ready' ? '#dcfce7' : '#fef9c3',
                        color: doc.status === 'ready' ? '#166534' : '#854d0e',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        textTransform: 'capitalize'
                      }}>
                        {doc.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>{new Date(doc.created_at).toLocaleDateString()}</td>
                    {isAdmin && (
                      <td style={{ padding: '12px' }}>
                        <button 
                          onClick={() => handleDelete(doc.id)}
                          className="delete-btn"
                          title="Delete Document"
                          style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
};

export default Documents;
