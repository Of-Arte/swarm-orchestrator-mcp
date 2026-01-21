import React from 'react';
import { motion } from 'framer-motion';
import { Database, ShieldCheck, Cpu, History, Terminal } from 'lucide-react';
import { useSwarmData } from '../hooks/useSwarmData';

const Memory = () => {
  const { data: memory, loading, error } = useSwarmData('/memory');

  if (loading) return <div className="page-content">Loading memory bank...</div>;
  if (error) return <div className="page-content">Error loading memory.</div>;

  const provenance = memory?.provenance || [];
  const workerModels = memory?.worker_models || {};
  const toolchain = memory?.toolchain || {};
  const stack = memory?.stack || {};

  return (
    <div className="page-content">
      <h1 className="gradient-text">Memory & Provenance</h1>
      
      <div className="stats-grid">
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <ShieldCheck size={24} color="#10b981" />
            <h3 style={{ margin: 0 }}>System Integrity</h3>
          </div>
          <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
            {provenance.length} Audit Events Recorded
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '8px' }}>
            Cryptographic signatures verified via local lifecycle.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Cpu size={24} color="#6366f1" />
            <h3 style={{ margin: 0 }}>Active Models</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
             {Object.entries(workerModels).slice(0, 3).map(([role, model]) => (
               <div key={role} style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between' }}>
                 <span style={{ color: 'var(--text-secondary)' }}>{role}:</span>
                 <span style={{ fontWeight: 'bold' }}>{model}</span>
               </div>
             ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginTop: '24px' }}>
        {/* Provenance Log */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <History size={24} color="var(--accent-primary)" />
            <h2 style={{ margin: 0, fontSize: '1.5rem' }}>Provenance Log</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {provenance.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No provenance events recorded yet.</p>
            ) : (
              provenance.map((event, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  style={{ 
                    padding: '16px', 
                    background: 'rgba(255,255,255,0.02)', 
                    borderRadius: '12px',
                    border: '1px solid var(--border-glass)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 'bold', color: 'var(--accent-primary)' }}>{event.action.toUpperCase()}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.9rem' }}>
                    Agent: <code style={{ color: 'var(--accent-secondary)' }}>{event.agent_id}</code> ({event.role})
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Ref: {event.artifact_ref || 'N/A'}
                  </div>
                </motion.div>
              )).reverse() // Show newest first
            )}
          </div>
        </div>

        {/* Stack Info */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <Terminal size={20} color="#ec4899" />
              <h3 style={{ margin: 0 }}>Stack Identity</h3>
            </div>
            <div style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Language: </span>
                <span style={{ fontWeight: 'bold' }}>{stack.primary_language || 'Detecting...'}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Toolchain: </span>
                <span style={{ fontWeight: 'bold' }}>{stack.toolchain_variant || 'N/A'}</span>
              </div>
              <div style={{ marginTop: '8px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Frameworks:</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {stack.frameworks?.map(f => (
                    <span key={f} style={{ 
                      fontSize: '0.7rem', 
                      padding: '2px 8px', 
                      background: 'rgba(99, 102, 241, 0.2)', 
                      borderRadius: '10px',
                      color: 'var(--accent-primary)'
                    }}>{f}</span>
                  ))}
                  {(!stack.frameworks || stack.frameworks.length === 0) && '-'}
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <Database size={20} color="#a855f7" />
              <h3 style={{ margin: 0 }}>Toolchain Configuration</h3>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              {toolchain.version ? `v${toolchain.version} Active` : 'No toolchain active'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Memory;
