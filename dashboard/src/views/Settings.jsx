import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Bell, Shield, Palette, Layout, Save } from 'lucide-react';

const Settings = () => {
  return (
    <div className="page-content">
      <h1 className="gradient-text">System Settings</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <Palette size={24} color="#6366f1" />
            <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Appearance</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>Glassmorphism Intensity</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Adjust backdrop blur level</div>
              </div>
              <input type="range" style={{ accentColor: 'var(--accent-primary)' }} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>Theme Mode</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Dark mode is default</div>
              </div>
              <div className="glass-panel" style={{ padding: '4px 12px', fontSize: '0.8rem', background: 'rgba(99, 102, 241, 0.1)' }}>
                Deep Ocean (Active)
              </div>
            </div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <Shield size={24} color="#10b981" />
            <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Security & API</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>Read-Only Mode</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Prevent file modifications</div>
              </div>
              <div style={{ width: '40px', height: '20px', background: 'rgba(255,255,255,0.1)', borderRadius: '10px', position: 'relative' }}>
                <div style={{ position: 'absolute', right: '2px', top: '2px', width: '16px', height: '16px', background: 'white', borderRadius: '50%' }}></div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>API Endpoint</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Local Swarm Server URL</div>
              </div>
              <code style={{ fontSize: '0.8rem', padding: '4px 8px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }}>
                http://localhost:8000/api
              </code>
            </div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <Bell size={24} color="#f59e0b" />
            <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Notifications</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>Task Completion</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Alert when a task finishes</div>
              </div>
              <input type="checkbox" defaultChecked />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>Audit Alerts</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Critical security notifications</div>
              </div>
              <input type="checkbox" defaultChecked />
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '32px', display: 'flex', justifyContent: 'flex-end' }}>
        <button 
          className="glass-panel" 
          style={{ 
            padding: '12px 24px', 
            background: 'var(--accent-primary)', 
            color: 'white', 
            border: 'none', 
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontWeight: 600
          }}
        >
          <Save size={18} />
          Save Configurations
        </button>
      </div>
    </div>
  );
};

export default Settings;
