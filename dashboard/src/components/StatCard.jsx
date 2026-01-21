import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ icon: Icon, label, value, color, delay = 0 }) => {
  return (
    <motion.div 
      className="glass-panel stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
    >
      <div className="stat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="stat-icon-bg" style={{ 
          background: `${color}20`, 
          padding: '10px', 
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Icon size={24} color={color} />
        </div>
        {/* Optional sparkline or trend identifier could go here */}
      </div>
      
      <div style={{ marginTop: '16px' }}>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </motion.div>
  );
};

export default StatCard;
