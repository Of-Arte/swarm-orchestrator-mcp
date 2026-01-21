import React from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle, XCircle, PlayCircle, Hash } from 'lucide-react';

const STATUS_CONFIG = {
  PENDING: { color: '#94a3b8', icon: Clock, label: 'Pending' },
  RUNNING: { color: '#3b82f6', icon: PlayCircle, label: 'Running' },
  COMPLETED: { color: '#22c55e', icon: CheckCircle, label: 'Completed' },
  FAILED: { color: '#ef4444', icon: XCircle, label: 'Failed' },
};

const TaskCard = ({ task }) => {
  const status = STATUS_CONFIG[task.status] || STATUS_CONFIG.PENDING;
  const StatusIcon = status.icon;

  return (
    <motion.div 
      className="glass-panel"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px', cursor: 'pointer' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ 
          background: 'rgba(255,255,255,0.05)', 
          padding: '4px 8px', 
          borderRadius: '6px', 
          fontSize: '0.8rem', 
          fontFamily: 'monospace',
          color: 'var(--text-secondary)',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <Hash size={12} />
          {task.id.substring(0, 8)}
        </div>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '6px', 
          color: status.color,
          fontSize: '0.9rem',
          fontWeight: 600,
          background: `${status.color}15`,
          padding: '4px 10px',
          borderRadius: '20px'
        }}>
          <StatusIcon size={14} />
          {status.label}
        </div>
      </div>
      
      <h3 style={{ fontSize: '1.1rem', lineHeight: '1.4' }}>
        {task.goal || task.description || "No description provided"}
      </h3>
      
      <div style={{ 
        marginTop: 'auto', 
        paddingTop: '12px', 
        borderTop: '1px solid var(--border-glass)',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.85rem',
        color: 'var(--text-secondary)'
      }}>
        <span>Task Type: {task.type || 'Generic'}</span>
      </div>
    </motion.div>
  );
};

export default TaskCard;
