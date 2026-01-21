import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Book, Github, Zap, Shield, Cpu, Network, ChevronRight, FileText } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api';

const DocsPage = () => {
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [docContent, setDocContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableDocs, setAvailableDocs] = useState([]);

  useEffect(() => {
    fetchDocsList();
  }, []);

  const fetchDocsList = async () => {
    try {
      const response = await fetch(`${API_BASE}/docs`);
      if (!response.ok) throw new Error('Failed to fetch docs list');
      const data = await response.json();
      // Map icons back to the data
      const withIcons = data.map(doc => ({
        ...doc,
        icon: doc.id.includes('/') ? Network : FileText
      }));
      setAvailableDocs(withIcons);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (selectedDoc) {
      fetchDoc(selectedDoc);
    }
  }, [selectedDoc]);

  const fetchDoc = async (filename) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/docs/${filename}`);
      if (!response.ok) throw new Error('Failed to fetch document');
      const data = await response.json();
      setDocContent(data.content);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const LandingPage = () => (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 className="gradient-text" style={{ fontSize: '3rem', marginBottom: '16px' }}>
          Swarm Orchestrator
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
          Multi-Agent Task Orchestration with Algorithmic Intelligence
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <a 
            href="https://github.com/AgentAgony/swarm" 
            target="_blank" 
            rel="noopener noreferrer"
            className="glass-panel"
            style={{ 
              padding: '12px 24px', 
              textDecoration: 'none', 
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: 600
            }}
          >
            <Github size={20} />
            View on GitHub
          </a>
          <button 
            onClick={() => setSelectedDoc('README.md')}
            className="glass-panel"
            style={{ 
              padding: '12px 24px', 
              background: 'var(--accent-primary)',
              color: 'white',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              borderRadius: '12px'
            }}
          >
            Get Started
          </button>
        </div>
      </div>

      {/* Features Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '48px' }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <Zap size={32} color="#6366f1" style={{ marginBottom: '12px' }} />
          <h3 style={{ marginBottom: '8px' }}>Fast Indexing</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Multi-threaded codebase indexing with HippoRAG graph persistence
          </p>
        </div>
        
        <div className="glass-panel" style={{ padding: '24px' }}>
          <Network size={32} color="#a855f7" style={{ marginBottom: '12px' }} />
          <h3 style={{ marginBottom: '8px' }}>Knowledge Graph</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            AST-based dependency analysis with PageRank retrieval
          </p>
        </div>
        
        <div className="glass-panel" style={{ padding: '24px' }}>
          <Cpu size={32} color="#ec4899" style={{ marginBottom: '12px' }} />
          <h3 style={{ marginBottom: '8px' }}>Algorithmic Workers</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Debate Engine, Git Worker, CRDT Merger, and more
          </p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '32px' }}>
        <h2 style={{ marginBottom: '24px' }}>Explore Documentation</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {availableDocs.map(doc => (
            <button
              key={doc.id}
              onClick={() => setSelectedDoc(doc.id)}
              className="glass-panel"
              style={{
                padding: '20px',
                textAlign: 'left',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-primary)',
                transition: 'all 0.2s'
              }}
            >
              <doc.icon size={24} color="var(--accent-primary)" />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{doc.label}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>View file content</div>
              </div>
              <ChevronRight size={20} color="var(--text-secondary)" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="page-content" style={{ display: 'flex', gap: '32px', height: '100%', overflow: 'hidden' }}>
      {/* Sidebar for Docs */}
      {selectedDoc && (
        <div style={{ width: '200px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button 
            onClick={() => setSelectedDoc(null)}
            style={{
              padding: '12px',
              textAlign: 'left',
              background: 'transparent',
              border: 'none',
              color: 'var(--accent-primary)',
              cursor: 'pointer',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '16px'
            }}
          >
            <ChevronRight size={16} style={{ transform: 'rotate(180deg)' }} />
            Back to Home
          </button>
          {availableDocs.map(doc => (
            <button
              key={doc.id}
              onClick={() => setSelectedDoc(doc.id)}
              style={{
                padding: '10px 16px',
                textAlign: 'left',
                background: selectedDoc === doc.id ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                border: 'none',
                color: selectedDoc === doc.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: selectedDoc === doc.id ? 600 : 400
              }}
            >
              {doc.label}
            </button>
          ))}
        </div>
      )}

      {/* Content Area */}
      <div style={{ flex: 1, overflowY: 'auto', paddingRight: '16px' }}>
        {!selectedDoc ? (
          <LandingPage />
        ) : (
          <div className="glass-panel" style={{ padding: '40px', minHeight: '100%' }}>
            {loading ? (
              <p>Loading document...</p>
            ) : error ? (
              <p style={{ color: '#ef4444' }}>Error: {error}</p>
            ) : (
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {docContent}
                </ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocsPage;
