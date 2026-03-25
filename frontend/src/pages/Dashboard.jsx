import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { MessageSquare, Clock, Users, BarChart3 } from 'lucide-react';

const Dashboard = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDebugData = async () => {
    try {
      const token = await getToken();
      const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const api_base = isLocal ? `http://${window.location.hostname}:8001` : '';

      const res = await fetch(`${api_base}/api/analytics/admin/debug`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Error fetching debug data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDebugData();
  }, []);

  if (loading) return <div className="loading-state">Loading debug info...</div>;

  return (
    <div className="dashboard-container" style={{ padding: '40px' }}>
      <header className="page-header" style={{ padding: '0 0 32px 0' }}>
        <h2>Admin Debug Dashboard</h2>
        <p className="small" style={{ color: 'var(--text-secondary)' }}>Minimal verification system</p>
      </header>

      {/* Stats Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '40px' }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '24px' }}>
          <Users size={32} color="var(--accent-color)" />
          <div>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>{stats?.total_users || 0}</div>
            <div className="small" style={{ color: 'var(--text-secondary)' }}>Total Users</div>
          </div>
        </div>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '24px' }}>
          <MessageSquare size={32} color="var(--accent-color)" />
          <div>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>{stats?.total_queries || 0}</div>
            <div className="small" style={{ color: 'var(--text-secondary)' }}>Total Queries</div>
          </div>
        </div>
      </div>

      {/* Recent Queries Section */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Clock size={24} color="var(--accent-color)" />
          <h3 style={{ margin: 0 }}>Recent Customer Queries (Last 5)</h3>
        </div>
        <div className="table-wrapper">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '12px' }}>Email</th>
                <th style={{ padding: '12px' }}>Company</th>
                <th style={{ padding: '12px' }}>Question</th>
                <th style={{ padding: '12px' }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {stats?.recent_queries?.map((q, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px', fontSize: '13px' }}>{q.email}</td>
                  <td style={{ padding: '12px' }}>{q.company}</td>
                  <td style={{ padding: '12px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {q.question}
                  </td>
                  <td style={{ padding: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {new Date(q.created_at).toLocaleString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}
                  </td>
                </tr>
              ))}
              {(!stats?.recent_queries || stats.recent_queries.length === 0) && (
                <tr><td colSpan="4" style={{ padding: '24px', textAlign: 'center' }}>No queries found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
