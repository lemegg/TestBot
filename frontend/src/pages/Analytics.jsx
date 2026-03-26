import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';

const Analytics = () => {
  const [activeTab, setActiveTab] = useState('top-queries');
  const [range, setRange] = useState('weekly');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { getToken } = useAuth();

  const downloadCSV = (data, filename, headers) => {
    if (!data || data.length === 0) return;

    // Create CSV content
    const csvRows = [];
    
    // Add headers
    csvRows.push(headers.join(','));

    // Add data rows
    for (const row of data) {
      const values = headers.map(header => {
        // Map UI header names to data keys
        const keyMap = {
          'Rank': 'rank',
          'Query': 'query',
          'Count': 'count',
          'Pos %': 'positive_percent',
          'Neg %': 'negative_percent',
          'Timestamp': 'timestamp',
          'User': 'email',
          'Company': 'company',
          'Mobile Number': 'phone_number',
          'Orders Shipped': 'orders_shipped',
          'Feedback': 'feedback'
        };
        
        const key = keyMap[header] || header.toLowerCase();
        let val = row[key];
        
        // Handle special formatting
        if (header === 'Timestamp' && val) {
          val = new Date(val).toLocaleString();
        }
        if ((header === 'Pos %' || header === 'Neg %') && val !== null && val !== undefined) {
          val = `${val}%`;
        }
        
        // Escape quotes and commas
        const escaped = ('' + (val || '—')).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }

    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      
      const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const api_base = isLocal ? `http://${window.location.hostname}:8001` : '';
      
      let url = `${api_base}/api/analytics/top-queries?range=${range}`;
      if (activeTab === 'query-log') {
        url = `${api_base}/api/analytics/query-log/monthly`;
      } else if (activeTab === 'sop-missed') {
        url = `${api_base}/api/analytics/sop-missed`;
      }

      try {
        const token = await getToken();
        const response = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
          if (response.status === 403) throw new Error('Not authorized to access analytics');
          throw new Error('Failed to fetch data');
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [range, activeTab, getToken]);

  // Handle tab switch - clear data to avoid showing old table format while loading new one
  const handleTabChange = (tab) => {
    if (tab !== activeTab) {
      setData(null);
      setActiveTab(tab);
    }
  };

  if (error) return <div className="dashboard-error">Access Denied: {error}</div>;

  return (
    <div className="main-content">
      <header className="page-header">
        <h2>Knowledge Analytics</h2>
      </header>
      
      <div className="documents-container" style={{ padding: '24px 32px' }}>
        <header className="dashboard-header" style={{ marginBottom: 24 }}>
          <div className="tabs">
            <button 
              className={`tab-btn ${activeTab === 'top-queries' ? 'active' : ''}`}
              onClick={() => handleTabChange('top-queries')}
            >
              Top Queries
            </button>
            <button 
              className={`tab-btn ${activeTab === 'query-log' ? 'active' : ''}`}
              onClick={() => handleTabChange('query-log')}
            >
              Monthly Query Log
            </button>
            <button 
              className={`tab-btn ${activeTab === 'sop-missed' ? 'active' : ''}`}
              onClick={() => handleTabChange('sop-missed')}
            >
              SOP Missed Queries
            </button>
          </div>
        </header>

        {loading ? (
          <div className="loading-state">Loading analytics data...</div>
        ) : (
          <div className="analytics-body">
            {activeTab === 'top-queries' && data?.top_queries && (
              <div className="queries-list">
                <div className="list-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3>Top 15 Queries ({range})</h3>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <button 
                      onClick={() => downloadCSV(data.top_queries, `top_queries_${range}`, ['Rank', 'Query', 'Count', 'Pos %', 'Neg %'])}
                      className="tab-btn"
                      style={{ padding: '6px 12px', fontSize: '13px', backgroundColor: '#f0f0f0' }}
                    >
                      📥 Download CSV
                    </button>
                    <div className="range-toggle">
                      <button className={range === 'weekly' ? 'active' : ''} onClick={() => setRange('weekly')}>Weekly</button>
                      <button className={range === 'monthly' ? 'active' : ''} onClick={() => setRange('monthly')}>Monthly</button>
                    </div>
                  </div>
                </div>
                <div className="docs-table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Rank</th>
                        <th>Query</th>
                        <th>Count</th>
                        <th>👍 Pos %</th>
                        <th>👎 Neg %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.top_queries.map((item, index) => (
                        <tr key={index}>
                          <td>{item.rank}</td>
                          <td>{item.query}</td>
                          <td>{item.count}</td>
                          <td>{item.positive_percent !== null ? `${item.positive_percent}%` : '—'}</td>
                          <td>{item.negative_percent !== null ? `${item.negative_percent}%` : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'query-log' && data?.logs && (
              <div className="queries-list">
                <div className="list-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3>Monthly Query Log (Last 30 Days)</h3>
                  <button 
                    onClick={() => downloadCSV(data.logs, 'monthly_query_log', ['Query', 'Timestamp', 'User', 'Company', 'Mobile Number', 'Orders Shipped', 'Feedback'])}
                    className="tab-btn"
                    style={{ padding: '6px 12px', fontSize: '13px', backgroundColor: '#f0f0f0' }}
                  >
                    📥 Download CSV
                  </button>
                </div>
                <div className="docs-table-container">
                  <div className="scrollable-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Query</th>
                          <th>Timestamp</th>
                          <th>User</th>
                          <th>Company</th>
                          <th>Mobile Number</th>
                          <th>Orders Shipped</th>
                          <th>Feedback</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.logs.map((log, index) => (
                          <tr key={index}>
                            <td>{log.query}</td>
                            <td style={{ whiteSpace: 'nowrap' }}>{new Date(log.timestamp).toLocaleString()}</td>
                            <td>{log.email}</td>
                            <td>{log.company}</td>
                            <td>{log.phone_number || '—'}</td>
                            <td>{log.orders_shipped || '—'}</td>
                            <td style={{ textAlign: 'center' }}>
                              {log.feedback === 'like' ? '👍' : log.feedback === 'dislike' ? '👎' : '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'sop-missed' && data?.logs && (
              <div className="queries-list">
                <div className="list-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3>SOP Missed Queries (Information Not Found)</h3>
                  <button 
                    onClick={() => downloadCSV(data.logs, 'sop_missed_queries', ['Query', 'Timestamp', 'User', 'Company', 'Mobile Number', 'Orders Shipped'])}
                    className="tab-btn"
                    style={{ padding: '6px 12px', fontSize: '13px', backgroundColor: '#f0f0f0' }}
                  >
                    📥 Download CSV
                  </button>
                </div>
                <div className="docs-table-container">
                  <div className="scrollable-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Query</th>
                          <th>Timestamp</th>
                          <th>User</th>
                          <th>Company</th>
                          <th>Mobile Number</th>
                          <th>Orders Shipped</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.logs.map((log, index) => (
                          <tr key={index}>
                            <td>{log.query}</td>
                            <td style={{ whiteSpace: 'nowrap' }}>{new Date(log.timestamp).toLocaleString()}</td>
                            <td>{log.email}</td>
                            <td>{log.company}</td>
                            <td>{log.phone_number || '—'}</td>
                            <td>{log.orders_shipped || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;
